# This is a sample Python script.

# Press ⇧F10 to execute it or replace it with your code.
# Press Double ⇧ to search everywhere for classes, files, tool windows, actions, and settings.
from selenium.common.exceptions import TimeoutException
# "strain_keywords": ["haze", "skywalker", "sky walker", "afghan","pakistan", "hindu", "maui","afgoo" ,"hindi","diesel","crack", "cheese","dixie","khalifa", "syrup" ]
class Workbook:
    def __init__(self, name):
        self.sheets =[]
        self.workbook_name=f'{name}'
    def write_workbook(self):

        writer = ExcelWriter(self.workbook_name)

        for filename in self.sheets:
            df_csv = pd.read_csv(filename)

            (_, f_name) = os.path.split(filename)
            (f_shortname, _) = os.path.splitext(f_name)
            df_csv.to_excel(writer,filename.split('/')[-1].split('__')[0], index=False)
        writer.save()
global_workbook = Workbook(module_config['report_file'].replace('{date}', file_suffix).replace("{location}", module_config['location'].split(',')[0]))
def combine_outputs(pids, type):
    '''
    This function combines a series of output csvs into a single file. This is required as this script is multi-processed and issues can occur writing to the same file
    :param pids: the list of child processes that have written files
    :param environment: the environment the files are written in. this corresponds to a directory name in extracts/
    :return:
    '''
    print(f"Combining {len(pids)} .csv files from child processes into a singular extract")
    pass
    rows = []
    for i in range(0, len(pids)):
        print(f"Processing {type}{pids[i]}.csv")
        if i==0:
            #base case
            if f"{type}{pids[i]}.csv" in os.listdir():
                rows=read_csv(f"{type}{pids[i]}.csv")
        else:
            print(f"reading from temp file {type}{pids[i]}.csv")
            if f"{type}{pids[i]}.csv" in os.listdir():
                tmp_rows = read_csv(f"{type}{pids[i]}.csv")
                for i in range(1, len(tmp_rows)):
                    rows.append(tmp_rows[i])


    print(f"writing extraction file to {type}.csv")
    write_csv(f'{type}.csv',rows)
def build_webdriver():
    CHROME_PATH = '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome'
    CHROMEDRIVER_PATH ='../chromedriver'
    WINDOW_SIZE = "1920,1080"

    chrome_options = Options()
    # chrome_options.headless=True
    # chrome_options.add_argument("--headless")
    # chrome_options.add_argument("--start-minimized")
    chrome_options.binary_location = '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome'

    driver = webdriver.Chrome(executable_path='../chromedriver', chrome_options=chrome_options)
    # driver = webdriver.Chrome('../chromedriver')
    driver.get("https://dutchie.com/")
    age_restriction_btn = driver.find_element(By.CSS_SELECTOR, 'button[data-test="age-restriction-yes"]')
    age_restriction_btn.click()
    return driver
def write_csv(filename, rows):
    with open(filename  , 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerows(rows)
    print(f"Wrote file {filename}")
    global_workbook.sheets.append(filename)
def print_hi(name):
    # Use a breakpoint in the code line below to debug your script.
    print(f'Hi, {name}')  # Press ⌘F8 to toggle the breakpoint.


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    print_hi('PyCharm')

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
