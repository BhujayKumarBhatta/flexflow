from flexflow.configs.prodconf import flexflow_configs
from .kafka_listener import Klistener


def main():
    print("listener to listen msg from comparator ************************************")
    invl = Klistener(flexflow_configs)
    result = invl._get_msg_n_trigger_action()
    print(result)