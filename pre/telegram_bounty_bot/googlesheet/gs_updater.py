"""
Updates google sheet for this bounty program
"""

import pygsheets

class UpdateSheet(object):
    def __init__(self, path, worksheet_name, sheet_name):
        self.client = pygsheets.authorize(service_file=path)
        try:
            self.worksheet = self.client.open(worksheet_name)
            self.sheet = self.worksheet.worksheet_by_title(sheet_name)
        except Exception as e:
            print('An exception occured')
            self.worksheet = self.client.create(worksheet_name)
            self.sheet = self.worksheet.add_worksheet(sheet_name)
            #self.sheet.update_cells('A1', [['s/n', 'Telegram Username', 'Number of weeks completed', 'Active Status', 'ETH Wallet Address']])
    
    def share_everyone(self):
        self.worksheet.share('anyone')
        return self.sheet.url

    def update_sheet(self, data_set):
        """
        data_set = [
            ['s/n, 'username', 'No of wks compld', 'Status],
            ['1', 'test_user', '1', 'Active']
        ]
        """
        self.sheet.update_cells('A2:F', data_set)

    def get_sheet_url(self):
        return self.sheet.url

def main():
    """Test this script"""
    google_sheet = UpdateSheet('client_secret.json', 'Dalecoin.org', 'Dalc Bounty List')
    print('sheet created/fetched')
    google_sheet.share_everyone()
    print('sheet shared')
    data_set = [
        ['1', 'test_user1', '1', 'Active'],
        ['2', 'test_user2', '2', 'Not Active']
    ]
    

    google_sheet.update_sheet(data_set)
    print('sheet updated')
    print(google_sheet.get_sheet_url())
    print('done')
if __name__ == '__main__':
    main()
