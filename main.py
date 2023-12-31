from collections import defaultdict
from typing import List

from db_controller import SQLiteDataBaseController


def unwind_list_of_tuples(sequence: List):
    return list(
        sum(sequence, ())
    )

def get_distinct_projects(db_controller: SQLiteDataBaseController):
    return unwind_list_of_tuples(
        db_controller.select_distinct(field='project_id', table='domains'))

def get_substrings_on_levels(domains: List):
    substrings_on_levels = {e: defaultdict(int) for e in range(6)}
    for domain in domains:
        levels = list(reversed(domain.split('.')))
        for i, level in enumerate(levels):
            substrings_on_levels[i][levels[i]] += 1
    return substrings_on_levels

def operate_projects(db_controller: SQLiteDataBaseController, projects: List):
    return_data = []
    for project_id in projects:
        domains = unwind_list_of_tuples(
            db_controller.select_col_by_equal_cond(
                field='name',
                table='domains',
                eq_field='project_id',
                eq_value=project_id,
            )
        )
        split_instance = domains[0].split('.')
        root = f"\.{split_instance[-2]}\.{split_instance[-1]}"
        substrings_on_levels = get_substrings_on_levels(domains)
        cases = []
        for i in range(5, 1, -1):
            ban_words = []
            levels_to_root = i - 2

            for k, v in substrings_on_levels[i].items():
                if v > 2:
                    ban_words.append(k)

            if ban_words:
                ban_str = '|'.join(ban_words)
                if levels_to_root > 0:
                    before_root = f'([a-zA-Z0-9_-])+\.{ban_str}\.' \
                                  f'{"([a-zA-Z0-9_-])+" * levels_to_root}'
                    cases.append(f'{before_root}{root}')
                else:
                    cases.append(f'([a-zA-Z0-9_-])+\.({ban_str})+{root}')

        return_data.append((project_id, '|'.join(cases)))
        return return_data

def main():
    db_controller = SQLiteDataBaseController(db_file='domains.db')
    distinct_projects = get_distinct_projects(db_controller=db_controller)
    insert_data = operate_projects(db_controller=db_controller,
                                   projects=distinct_projects)
    db_controller.write(table='rules', data=insert_data)
    
if __name__ == "__main__":
    main()