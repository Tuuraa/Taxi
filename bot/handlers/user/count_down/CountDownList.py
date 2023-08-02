class CountDownList:

    def __init__(self, *args, **kwargs):
        self.args = args
        self.kwargs = kwargs

        self.__count_down_list = []

    @property
    def count_down_list(self):
        return self.__count_down_list

    def add_count_down(self, current_count_down):
        self.__count_down_list.append(current_count_down)

    def remove_count_down(self, current_count_down):
        self.__count_down_list.remove(current_count_down)

    def get_element_from_count_down(self, id_by_element):
        try:
            for element_from_count_down in self.__count_down_list:
                if element_from_count_down == id_by_element:
                    return self.__count_down_list[id_by_element]
        finally:
            print("Exception from 'get_element_from_count_down'")



