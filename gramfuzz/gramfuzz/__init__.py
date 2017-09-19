#!/usr/bin/env python
# encoding: utf-8


"""
This module defines the main ``GramFuzzer`` class through
which rules are defined and rules are randomly generated.
"""


from collections import deque
import copy
import gc
import os
import sys


import gramfuzz.errors as errors
import gramfuzz.rand as rand
import gramfuzz.utils as utils


__version__ = "1.2.0"


class GramFuzzer(object):
    """
    ``GramFuzzer`` is a singleton class that is used to
    hold rule definitions and to generate grammar rules from a specific
    category at random.
    """

    defs = {}
    """Rule definitions by category. E.g. ::
        
        {
            "category": {
                "rule1": [<Rule1Def1>, <Rule1Def2>],
                "rule2": [<Rule2Def1>, <Rule2Def2>],
                ...
            }
        }
    """

    no_prunes = {}
    """Rules that have specifically asked not to be pruned,
    even if the rule can't be reached.
    """

    cat_groups = {}
    """Used to store where rules were defined in. E.g. if a rule
    ``A`` was defined using the category ``alphabet_rules`` in a file
    called ``test_rules.py``, it would show up
    in ``cat_groups`` as: ::

        {
            "alphabet_rules": {
                "test_rules": ["A"]
            }
        }

    This lets the user specify probabilities/priorities for rules coming
    from certain grammar files
    """

    __instance__ = None
    @classmethod
    def instance(cls):
        """Return the singleton instance of the ``GramFuzzer``
        """
        if cls.__instance__ is None:
            cls()
        return cls.__instance__


    def __init__(self):
        """Create a new ``GramFuzzer`` instance
        """
        GramFuzzer.__instance__ = self
        self.defs = {}
        self.no_prunes = {}
        self.cat_groups = {}
        self.cat_group_defaults = {}

        # used during rule generation to keep track of things
        # that can be reverted if things go wrong
        self._staged_defs = None

        # the last-defined preferred category-group names
        self._last_prefs = None

        # the last-defined rule definition names derived from the ``_last_prefs``
        self._last_pref_keys = None

        # a simple flag to tell if data needs to be auto processed or not
        self._rules_processed = False
    
    def load_grammar(self, path):
        """Load a grammar file (python file containing grammar definitions) by
        file path. When loaded, the global variable ``GRAMFUZZER`` will be set
        within the module. This is not always needed, but can be useful.

        :param str path: The path to the grammar file
        """
        if not os.path.exists(path):
            raise Exception("path does not exist: {!r}".format(path))
        
        # this will let grammars reference eachother with relative
        # imports.
        #
        # E.g.:
        #     grams/
        #         gram1.py
        #         gram2.py
        #
        # gram1.py can do "import gram2" to require rules in gram2.py to
        # be loaded
        grammar_path = os.path.dirname(path)
        if grammar_path not in sys.path:
            sys.path.append(grammar_path)

        with open(path, "r") as f:
            data = f.read()
        code = compile(data, path, "exec")

        locals_ = {"GRAMFUZZER": self, "__file__": path}
        exec(code) in locals_

        if "TOP_CAT" in locals_:
            cat_group = os.path.basename(path).replace(".py", "")
            self.set_cat_group_top_level_cat(cat_group, locals_["TOP_CAT"])

    def set_max_recursion(self, level):
        """Set the maximum reference-recursion depth (not the Python system maximum stack
        recursion level). This controls how many levels deep of nested references are allowed
        before gramfuzz attempts to generate the shortest (reference-wise) rules possible.

        :param int level: The new maximum reference level
        """
        import gramfuzz.fields
        gramfuzz.fields.Ref.max_recursion = level

    def preprocess_rules(self):
        """Calculate shortest reference-paths of each rule (and Or field),
        and prune all unreachable rules.
        """
        to_prune = self._find_shortest_paths()
        self._prune_rules(to_prune)

        self._rules_processed = True

    def _find_shortest_paths(self):
        leaf_rules = deque()
        non_leaf_rules = deque()
        rule_ref_lengths = {}

        # first find all rule definitions that *don't* have
        # any references - these are the leaf nodes
        for cat in self.defs.keys():
            for rule_name, rules in self.defs.get(cat, {}).items():
                for rule in rules:
                    refs = self._collect_refs(rule)
                    if len(refs) == 0:
                        leaf_rules.append(rule)
                        rule_ref_lengths[cat + "-:-" + rule.name] = (0, [rule])
                    else:
                        non_leaf_rules.append((cat, rule))

        # for every referenced rule, determine how many steps away
        # from a leaf node it is
        post_process = deque()
        unprocessed_count = 0
        while len(non_leaf_rules) > 0:
            # this means we've looped twice over everything
            # without being able to process the remaining nodes
            if unprocessed_count // len(non_leaf_rules) == 2:
                break

            cat, curr_rule = non_leaf_rules.popleft()

            ref_length = self._process_shortest_ref(cat, curr_rule, rule_ref_lengths)
            if ref_length is None:
                non_leaf_rules.append((cat, curr_rule))
                unprocessed_count += 1
                continue

            unprocessed_count = 0

            ref_key = cat + "-:-" + curr_rule.name
            if ref_key not in rule_ref_lengths or ref_length < rule_ref_lengths[ref_key][0]:
                rule_ref_lengths[ref_key] = (ref_length, [curr_rule])
            elif ref_length == rule_ref_lengths[ref_key][0]:
                rule_ref_lengths[ref_key][1].append(curr_rule)

            post_process.append((cat, curr_rule))

        self._assign_or_shortest_vals(post_process, rule_ref_lengths)

        # these should be pruned
        return non_leaf_rules

    def _prune_rules(self, non_leaf_rules):
        for cat,rule in non_leaf_rules:
            if cat in self.no_prunes and rule.name in self.no_prunes[cat]:
                continue
            rule_list = self.defs.get(cat, {}).get(rule.name, [])
            rule_list.remove(rule)
            if len(rule_list) == 0:
                del self.defs.get(cat, {})[rule.name]

    def _assign_or_shortest_vals(self, fields, rule_ref_lengths):
        for cat,field in fields:
            self._process_shortest_ref(cat, field, rule_ref_lengths, assign_or=True)

    def _process_shortest_ref(self, cat, field, rule_ref_lengths, assign_or=False):
        import gramfuzz.fields as fields

        # strings, ints, hard-coded non-gramfuzz values
        if not isinstance(field, fields.Field) or getattr(field, "shortest_is_nothing", False):
            return 0

        # return None if it can't be determined yet
        if isinstance(field, fields.Or):
            min_ref = 0xffffff
            min_vals = []
            for val in field.values:
                val_ref = self._process_shortest_ref(
                    cat,
                    val,
                    rule_ref_lengths,
                    assign_or = assign_or,
                )
                if val_ref is None:
                    continue
                elif val_ref < min_ref:
                    min_ref = val_ref
                    min_vals = [val]
                elif val_ref == min_ref:
                    min_vals.append(val)

            if min_ref == 0xffffff:
                return None

            if assign_or:
                field.shortest_vals = min_vals

            return min_ref

        # these all be all refs from Ands, Joins, etc, while ignoring
        # any optional fields (since those will be ignored with shortest=True
        # set on a call to build()).
        #
        # Also for Defs, Ands, Joins, etc, we'll be returning the maximum
        # ref length, since every reference *must* be generated
        if hasattr(field, "values"):
            max_ref_length = -1
            for val in field.values:
                ref_val_length = self._process_shortest_ref(
                    cat,
                    val,
                    rule_ref_lengths,
                    assign_or = assign_or,
                )
                if ref_val_length is None:
                    return None
                if ref_val_length > max_ref_length:
                    max_ref_length = ref_val_length

            if max_ref_length == -1:
                return None
            return max_ref_length

        if isinstance(field, fields.Ref):
            ref_key = field.cat + "-:-" + field.refname
            ref_val = rule_ref_lengths.get(ref_key, (-1, []))[0]
            if ref_val == -1:
                return None
            ref_rule_val = rule_ref_lengths[ref_key][1][0]

            # if the referenced value is a native python type,
            # don't increment the reference value
            #
            # E.g. If it's a Ref("string"), and Def("string") doesn't contain
            # any references, don't increment the value
            if ref_val == 0 and len(self._collect_refs(ref_rule_val)) == 0:
                return 0
                
            # add one if the reference value is more than 0
            return ref_val + 1

        return None

    def _collect_refs(self, item_val, acc=None, no_opt=False):
        if acc is None:
            acc = deque()

        from gramfuzz.fields import Opt
        if no_opt and (isinstance(item_val, Opt) or item_val.shortest_is_nothing):
            return acc

        from gramfuzz.fields import Ref
        if isinstance(item_val, Ref):
            acc.append(item_val)

        if hasattr(item_val, "values"):
            for val in item_val.values:
                self._collect_refs(val, acc)

        return acc
    
    # --------------------------------------
    # public, but intended for internal use
    # --------------------------------------
    
    def add_definition(self, cat, def_name, def_val, no_prune=False, gram_file="default"):
        """Add a new rule definition named ``def_name`` having value ``def_value`` to
        the category ``cat``.

        :param str cat: The category to add the rule to
        :param str def_name: The name of the rule definition
        :param def_val: The value of the rule definition
        :param bool no_prune: If the rule should explicitly *NOT*
            be pruned even if it has been determined to be unreachable (default=``False``)
        :param str gram_file: The file the rule was defined in (default=``"default"``).
        """
        self._rules_processed = False

        self.add_to_cat_group(cat, gram_file, def_name)

        if no_prune:
            self.no_prunes.setdefault(cat, {}).setdefault(def_name, True)

        if self._staged_defs is not None:
            # if we're tracking changes during rule generation, add any new rules
            # to _staged_defs so they can be reverted if something goes wrong
            self._staged_defs.append((cat, def_name, def_val))
        else:
            self.defs.setdefault(cat, {}).setdefault(def_name, deque()).append(def_val)

    def set_cat_group_top_level_cat(self, cat_group, top_level_cat):
        """Set the default category when generating data from the grammars defined
        in cat group. *Note* a cat group is usually just the basename of the grammar
        file, minus the ``.py``.

        :param str cat_group: The category group to set the default top-level cat for
        :param str top_level_cat: The top-level (default) category of the cat group
        """
        self.cat_group_defaults[cat_group] = top_level_cat
    
    def add_to_cat_group(self, cat, cat_group, def_name):
        """Associate the provided rule definition name ``def_name`` with the
        category group ``cat_group`` in the category ``cat``.

        :param str cat: The category the rule definition was declared in
        :param str cat_group: The group within the category the rule belongs to
        :param str def_name: The name of the rule definition
        """
        self.cat_groups.setdefault(cat, {}).setdefault(cat_group, deque()).append(def_name)
    
    def get_ref(self, cat, refname):
        """Return one of the rules in the category ``cat`` with the name
        ``refname``. If multiple rule defintions exist for the defintion name
        ``refname``, use :any:`gramfuzz.rand` to choose a rule at random.

        :param str cat: The category to look for the rule in.
        :param str refname: The name of the rule definition. If the rule definition's name is
            ``"*"``, then a rule name will be chosen at random from within the category ``cat``.
        :returns: gramfuzz.fields.Def
        """
        if cat not in self.defs:
            raise errors.GramFuzzError("referenced definition category ({!r}) not defined".format(cat))
        
        if refname == "*":
            refname = rand.choice(self.defs[cat].keys())
            
        if refname not in self.defs[cat]:
            raise errors.GramFuzzError("referenced definition ({!r}) not defined".format(refname))

        return rand.choice(self.defs[cat][refname])


    def gen(self, num, cat=None, cat_group=None, preferred=None, preferred_ratio=0.5, max_recursion=None, auto_process=True):
        """Generate ``num`` rules from category ``cat``, optionally specifying
        preferred category groups ``preferred`` that should be preferred at
        probability ``preferred_ratio`` over other randomly-chosen rule definitions.

        :param int num: The number of rules to generate
        :param str cat: The name of the category to generate ``num`` rules from
        :param str cat_group: The category group (ie python file) to generate rules from. This
            was added specifically to make it easier to generate data based on the name
            of the file the grammar was defined in, and is intended to work with the
            ``TOP_CAT`` values that may be defined in a loaded grammar file.
        :param list preferred: A list of preferred category groups to generate rules from
        :param float preferred_ratio: The percent probability that the preferred
            groups will be chosen over randomly choosen rule definitions from category ``cat``.
        :param int max_recursion: The maximum amount to allow references to recurse
        :param bool auto_process: Whether rules should be automatically pruned and
            shortest reference paths determined. See :any:`gramfuzz.GramFuzzer.preprocess_rules`
            for what would automatically be done.
        """
        import gramfuzz.fields
        gramfuzz.fields.REF_LEVEL = 1

        if cat is None and cat_group is None:
            raise gramfuzz.errors.GramFuzzError("cat and cat_group are None, one must be set")

        if cat is None and cat_group is not None:
            if cat_group not in self.cat_group_defaults:
                raise gramfuzz.errors.GramFuzzError(
                    "cat_group {!r} did not define a TOP_CAT variable"
                )
            cat = self.cat_group_defaults[cat_group]
            if not isinstance(cat, basestring):
                raise gramfuzz.errors.GramFuzzError(
                    "cat_group {!r}'s TOP_CAT variable was not a string"
                )

        if auto_process and self._rules_processed == False:
            self.preprocess_rules()

        if max_recursion is not None:
            self.set_max_recursion(max_recursion)

        if preferred is None:
            preferred = []

        res = deque()
        cat_defs = self.defs[cat]

        # optimizations
        _res_append = res.append
        _res_extend = res.extend
        _choice = rand.choice
        _maybe = rand.maybe
        _val = utils.val

        keys = self.defs[cat].keys()

        self._last_pref_keys = self._get_pref_keys(cat, preferred)
        # be sure to set this *after* fetching the pref keys (above^)
        self._last_prefs = preferred

        total_errors = deque()
        total_gend = 0
        while total_gend < num:
            # use a rule definition from one of the preferred category
            # groups
            if len(self._last_pref_keys) > 0 and _maybe(preferred_ratio):
                rand_key = _choice(self._last_pref_keys)
                if rand_key not in cat_defs:
                    # TODO this means it was removed / pruned b/c it was unreachable??
                    # TODO look into this more
                    rand_key = _choice(list(keys))

            # else just choose a key at random from the category
            else:
                rand_key = _choice(list(keys))

            # pruning failed, this rule is not defined/reachable
            if rand_key not in cat_defs:
                continue

            v = _choice(cat_defs[rand_key])

            # not used directly by GramFuzzer, but could be useful
            # to subclasses of GramFuzzer
            info = {}

            pre = deque()
            self.pre_revert(info)
            val_res = None

            try:
                val_res = _val(v, pre)
            except errors.GramFuzzError as e:
                raise
                #total_errors.append(e)
                #self.revert(info)
                #continue
            except RuntimeError as e:
                print("RUNTIME ERROR")
                self.revert(info)
                continue

            if val_res is not None:
                _res_extend(pre)
                _res_append(val_res)

                total_gend += 1
                self.post_revert(cat, res, total_gend, num, info)

        return res
    
    def pre_revert(self, info=None):
        """Signal to begin saving any changes that might need to be reverted
        """
        self._staged_defs = deque()
    
    def post_revert(self, cat, res, total_num, num, info):
        """Commit any staged rule definition changes (rule generation went
        smoothly).
        """
        if self._staged_defs is None:
            return
        for cat,def_name,def_value in self._staged_defs:
            self.defs.setdefault(cat, {}).setdefault(def_name, deque()).append(def_value)
        self._staged_defs = None
    
    def revert(self, info=None):
        """Revert after a single def errored during generate (throw away all
        staged rule definition changes)
        """
        self._staged_defs = None

    def _get_pref_keys(self, cat, preferred):
        if preferred == self._last_prefs:
            pref_keys = self._last_pref_keys
        else:
            pref_keys = deque()
            for pref in preferred:
                if pref in self.cat_groups[cat]:
                    pref_keys.extend(self.cat_groups[cat][pref])
                elif pref in self.defs[cat]:
                    pref_keys.append(pref)

        return pref_keys
