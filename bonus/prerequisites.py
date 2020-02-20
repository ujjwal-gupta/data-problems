from collections import OrderedDict


class TaskExecutor:

    def __init__(self, relation_path, task_id_path):
        self.relation_path = relation_path
        self.task_id_path = task_id_path
        self.task_dependencies = self.__get_task_dependencies()

    def __get_task_dependencies(self):
        """ Builds dependency dictionary
        {
            <task1>: {<dependency1>, <dependency2>...}
            <task2>: set()
            .
            .
            .
        }

        :return: dependency dictionary
        """
        task_dependencies = {}

        with open(self.task_id_path) as tasks:
            for task in tasks.read().split(','):
                task_dependencies[task] = set()

        with open(self.relation_path) as relations:
            for relation in relations.readlines():
                [dependency, task] = relation.rstrip('\n').split('->')
                task_dependencies[task].add(dependency)

        return task_dependencies

    @staticmethod
    def __get_start_goal_task(question_path):
        """ Extracts starting tasks as a Set and goal task from question file

        """

        start = None
        goal = None
        with open(question_path) as question:
            for line in question.readlines():
                if line.startswith('starting task: '):
                    start = set(line.lstrip('starting task: ').rstrip('\n').split(','))
                elif line.startswith('goal task: '):
                    goal = line.lstrip('goal task: ').rstrip('\n')

        return start, goal

    def __visit_task_nodes(self, curr_node, start_nodes):
        """ Depth first recursive visit of dependency DAG with a direct return if no dependencies or node is a starting
        task

        :param curr_node: current node in recursion
        :param start_nodes: starting tasks set
        :return: visited nodes list
        """
        if curr_node in start_nodes:
            return [curr_node]

        visited_nodes = [curr_node]
        for dependency in self.task_dependencies[curr_node]:
            visited_nodes += self.__visit_task_nodes(dependency, start_nodes)

        return visited_nodes

    def get_task_order(self, question_path):
        """ Main function returning task execution order base on input question file

        :param question_path: question file path
        :return:
        """
        start, goal = self.__get_start_goal_task(question_path)
        task_dependency_track = self.__visit_task_nodes(goal, start)
        # Reverses order and then removes duplicates (keeping first occurrence)
        task_dependency_track = list(OrderedDict.fromkeys(task_dependency_track[::-1]))
        return ','.join(task_dependency_track)


if __name__ == '__main__':
    task_executor = TaskExecutor('relations.txt', 'task_ids.txt')
    task_order = task_executor.get_task_order('question.txt')

    print(task_order)
