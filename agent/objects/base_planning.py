import re
import itertools 
import copy
import pickle

from importlib import import_module
from base64 import b64encode
from objects.rule_set import RuleSet

class BasePlanningService:
    # Matches facts/variables.
    # Group 1 returns the trait, including any limits
    # Ex: '#{server.malicious.url}' => 'server.malicious.url'
    # Ex: '#{host.file.path[filters(technique=T1005,max=3)]}' => 'host.file.path[filters(technique=T1005,max=3)]'
    re_variable = re.compile(r'#{(.*?)}', flags=re.DOTALL)

    # Matches facts/variables that contain limits, denoted by brackets in the fact name.
    # Ex: Matches '#{host.file.path[filters(technique=T1005,max=3)]}'
    # Ex: Does not match: '#{server.malicious.url}'
    re_limited = re.compile(r'#{.*\[*\]}')

    # Matches the trait of a limited fact
    # Group 0 returns the trait excluding any limits
    # Ex: Does not match non-limited fact '#{server.malicious.url}'
    # Ex: #{host.file.path[filters(technique=T1005,max=3)]} => 'host.file.path'
    re_trait = re.compile(r'(?<=\{).+?(?=\[)')

    # Matches trait limits.
    # Group 0 returns the specific filters.
    # Ex: '#{host.file.path[filters(technique=T1005,max=3)]}' => 'technique=T1005,max=3'
    re_index = re.compile(r'(?<=\[filters\().+?(?=\)\])')

    def __init__(self):
        self._cached_requirement_modules = {}

    def is_global_variable(self, variable, agent):
        if variable.startswith('app.'):
            return True
        if variable.startswith('payload:'):
            return True
        if variable == 'payload':
            return True
        if variable in agent.RESERVED:
            return True
        if variable == 'origin_link_id':
            return True
        return False 
    
    @staticmethod
    def load_module(module_type, module_info):
        module = import_module(module_info['module'])
        return getattr(module, module_type)(module_info)
    
    @staticmethod
    def encode_string(s):
        return str(b64encode(s.encode()), 'utf-8')

    @staticmethod
    def _build_relevant_facts(variables, facts):
        """
        Create a list of facts which are relevant to the given ability's defined variables

        Returns: (list) of lists, with each inner list providing all known values for the corresponding fact trait
        """
        relevant_facts = []
        for v in variables:
            variable_facts = []
            for fact in [f for f in facts if f.trait == v.split('[')[0]]:
                variable_facts.append(fact)
            relevant_facts.append(variable_facts)
        return relevant_facts
    
    def _has_unset_variables(self, combo, variable_set):
        variables_present = [any(c.trait in var for c in combo) for var in variable_set]
        return not all(variables_present)
    
    def _is_missing_requirements(self, link, combo, operation):
        copy_used = list(link.used)
        link.used.extend(combo)
        missing = not (self._do_enforcements(link, operation))
        link.used = copy_used
        return missing

    def _do_enforcements(self, link, operation):
        """
        enforce any defined requirements on the link
        """
        for req_inst in link.ability['requirements']:
            for rel_match in req_inst['relationship_match']:
                module = req_inst['module'].split('.')
                plugin = module[1]
                requirement_name = module[-1]
                requirements_info = dict(module="requirements." + plugin + '.' + requirement_name, enforcements=rel_match)
                cache_key = str(requirements_info)
                try:
                    if cache_key not in self._cached_requirement_modules:
                        self._cached_requirement_modules[cache_key] = self.load_module('Requirement', requirements_info)
                    requirement = self._cached_requirement_modules[cache_key]
                    if not requirement.enforce(link, operation):
                        return False
                except Exception as e:
                    print("Error while do enforement: ", e)
        return True

    @staticmethod
    def _build_single_test_variant(copy_test, combo, executor):
        """
        Replace all variables with facts from the combo to build a single test variant
        """
        score, used = 0, list()
        for var in combo:
            score += (score + var.score)
            used.append(var)

            # Matches a complete fact with a given trait
            # Ex: Matches ${a}
            # Ex: Matches ${a.b.c}
            # Ex: Matches ${a.b.c[filters(max=3)]}
            pattern = r'#{(%s(?=[\[}]).*?)}' % re.escape(var.trait)
            re_variable = re.compile(pattern, flags=re.DOTALL)
            copy_test = re.sub(re_variable, str(var.escaped(executor)).strip().encode('unicode-escape').decode('utf-8'),
                               copy_test)
             
        return copy_test, score, used

    def apply_rules(self, facts):
        return [facts]

    def add_test_variants(self, links, agent, facts=(), rules=(), trim_unset_variables=False, trim_missing_requirements=False, operation=None):
        link_variants = []
        rule_set = RuleSet(rules=rules)
        for link in links:
            test = agent.replace(link.command)
            variables = set(x for x in re.findall(self.re_variable, test) if not self.is_global_variable(x, agent))

            relevant_facts = self._build_relevant_facts(variables, facts)
            valid_facts = [self._trim_by_limit(
                test,
                (rule_set.apply_rules(facts=fact_set))
            ) for fact_set in relevant_facts]
            combos = list(itertools.product(*valid_facts))

            if trim_unset_variables:
                combos = [combo for combo in combos if not self._has_unset_variables(combo, variables)]
    
            if trim_missing_requirements:
                combos = [combo for combo in combos if not self._is_missing_requirements(link, combo, operation)]
            
            for combo in combos:
                try:
                    copy_test = copy.copy(test)
                    variant, score, used = self._build_single_test_variant(copy_test, combo, link.executor.name)

                    copy_link = pickle.loads(pickle.dumps(link))    # nosec
                    copy_link.command = variant
                    copy_link.score = score
                    copy_link.used.extend(used) 
                    link_variants.append(copy_link)
                except Exception as ex:
                    print(f"Error while adding test variants: {ex}")
        
        if trim_unset_variables:
            links = self.remove_links_with_unset_variables(links)
        return self.sort_links(links + link_variants)
        
    def _trim_by_limit(self, decoded_test, facts):
        limited_facts = []
        for limit in re.findall(self.re_limited, decoded_test):
            limited = pickle.loads(pickle.dumps(facts))     # nosec
            trait = re.search(self.re_trait, limit).group(0).split('#{')[-1]

            limit_definitions = re.search(self.re_index, limit).group(0)
            if limit_definitions:
                for limiter in limit_definitions.split(','):
                    limited = self._apply_limiter(trait=trait, limiter=limiter.split('='), facts=limited)
            if limited:
                limited_facts.extend(limited)
        if limited_facts:
            return limited_facts
        return facts
    
    @staticmethod
    def _apply_limiter(trait, limiter, facts):
        if limiter[0] == 'max':
            return sorted([f for f in facts if f.trait == trait], key=lambda k: (-k.score))[:int(limiter[1])]
        if limiter[0] == 'technique':
            return [f for f in facts if f.technique == limiter[1]]

    @staticmethod
    def remove_links_with_unset_variables(links):
        """
        Remove any links that contain variables that have not been filled in.

        :param links:
        :return: updated list of links
        """
        links[:] = [s_link for s_link in links if not
                    BasePlanningService.re_variable.findall(s_link.command)]
        return links

    @staticmethod
    def sort_links(links):
        """Sort links by score and atomic ordering in adversary profile

        :param links: List of links to sort
        :type links: list(Link)
        :return: Sorted links
        :rtype: list(Link)
        """
        return sorted(links, key=lambda k: (-k.score))
