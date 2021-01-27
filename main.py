import locale
from dotenv import load_dotenv
import yvondirateldil

if __name__ == '__main__':
    locale.setlocale(locale.LC_ALL, 'fr_FR.UTF-8')
    # logging.basicConfig(stream=sys.stderr, level=logging.DEBUG)
    load_dotenv()

    yvondir_ateldil = yvondirateldil.YvondirAteldil()
    yvondir_ateldil.run()
