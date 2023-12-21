import sys
from time import sleep
import logging
import requests


main_logger = logging.getLogger()
main_logger.setLevel(logging.INFO)
handler = logging.StreamHandler(sys.stdout)
handler.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
main_logger.addHandler(handler)

def t_up():
    logging.info("started")
    # print("started")
    # thread1 = Thread(target=tor_ip_api, )
    # thread1.start()
    while True:
        try:
            torbulkexitlist = "torbulkexitlist.txt"
            exit_addresses = "exit-addresses.txt"

            try:
                logging.info("dling torbulkexitlist")
                dl_url = 'https://check.torproject.org/torbulkexitlist'
                r = requests.get(dl_url, allow_redirects=True)
                open(torbulkexitlist, 'wb').write(r.content)
            except:
                pass


            try:
                logging.info("dling exit-addresses")
                dl_url = 'https://check.torproject.org/exit-addresses'
                r = requests.get(dl_url, allow_redirects=True)
                open(exit_addresses, 'wb').write(r.content)
            except:
                pass

            sleep(60 * 60)
        except:
            pass
