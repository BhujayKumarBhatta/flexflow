from kafka import KafkaProducer
from kafka.errors import KafkaError
from json import  dumps


def preparekafkaresponse(wfc, response_list):
    kafka_response = {"request_id": wfc.request_id,
                      "wfcdict": wfc.to_dict(),
                      "msg_source": "paperhouse",
                      "response_list": response_list,
                      }
          
    return   kafka_response   


def notify_kafka(confobj, wfc, response_list):
    conf = confobj.yml
    kafka_response = preparekafkaresponse(wfc, response_list)
    ''' within the consumer itself this method produce  the processed resutl to kafka'''
    producer = KafkaProducer(bootstrap_servers=conf.get('kafka_servers'),
                      value_serializer=lambda x: 
                      dumps(x).encode('utf-8'))
#     kafka_response.pop('_id')
    future = producer.send('topic_paperhouse', value= kafka_response)
    # Block for 'synchronous' sends
    try:
        record_metadata = future.get(timeout=10)
        # Successful result returns assigned partition and offset
        print('...................',record_metadata.topic, 
              record_metadata.partition,
              record_metadata.offset,
              'Produced for paperhouse')
        print(kafka_response)      
    except KafkaError:
        # Decide what to do if produce request failed...
        #log.exception()
        print('failed to produce ')           
        
        
