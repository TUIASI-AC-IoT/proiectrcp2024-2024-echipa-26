from os import environ, listdir, system
from traceback import format_exc


from define import logger
from Router import Router
    



def main():
    try:
        
        IPSubnetList = []
        timeoutVals = dict()
        metric = dict()
        garbage = dict()
        
        ID = environ['ID']
        
        path = f'/home/tc/pr/cfg/r{ID}'
        for config in listdir(path):
            configPath = path+f'/{config}'
            file = open(configPath)
            lines = file.readlines()
            IPSubnetList.append((lines[2][3:-1],lines[3][7:-1]))
            
            timeoutVals[IPSubnetList[-1][0]] = int(lines[4].split('=')[1])
            metric[IPSubnetList[-1][0]] = int(lines[5].split('=')[1])
            garbage[IPSubnetList[-1][0]] = int(lines[6].split('=')[1])
            
        print(ID)
        print(IPSubnetList)
        return
        
        R = Router(IPSubnetList, timeoutVals, garbage, metric)
        R.start()
    except KeyboardInterrupt:
        try:
            R.shutdown()
        except BaseException as e:
            logger.error(format_exc())
    except BaseException as e:
        logger.error(format_exc())
        try:
            R.shutdown()
        except BaseException as e:
            logger.error(format_exc())
            exit(0)
        
        
if __name__ == "__main__":
    main()
    