import json
import xlsxwriter

# Load the JSON data
with open('hafta_audio_urls.json', 'r', encoding='utf-8') as f:
    episodes = json.load(f)

# Create an Excel workbook and worksheet
workbook = xlsxwriter.Workbook('hafta_episodes.xlsx')
worksheet = workbook.add_worksheet()

# Define the headers
headers = ['hafta_num', 'title', 'publishDate', 'summary', 'streamUrl', 'duration', 'cover']

# Write the headers
for col, header in enumerate(headers):
    worksheet.write(0, col, header)

# Write the episode data
for row, ep in enumerate(episodes, start=1):
    worksheet.write(row, 0, ep.get('hafta_num', ''))
    worksheet.write(row, 1, ep.get('title', ''))
    worksheet.write(row, 2, ep.get('publishDate', ''))
    worksheet.write(row, 3, ep.get('summary', ''))
    worksheet.write(row, 4, ep.get('streamUrl', ''))
    worksheet.write(row, 5, ep.get('duration', ''))
    worksheet.write(row, 6, ep.get('cover', ''))

workbook.close()

print('Excel file created: hafta_episodes.xlsx') 