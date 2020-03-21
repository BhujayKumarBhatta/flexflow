from flexflow.configs.prodconf import flexflow_configs
from .kafka_listener import Klistener
from flexflow.domains.domainlogics.workflow import Workflow

def main():
    print("listener to listen msg from comparator ************************************")
    invl = Klistener(flexflow_configs, Workflow)
    result = invl._get_msg_n_trigger_action()
    print(result)