import os
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter

def create_dummy_pdf(filename, year):
    c = canvas.Canvas(filename, pagesize=letter)
    c.drawString(100, 750, f"UDAAN Society Annual Report: {year}")
    c.drawString(100, 730, "This is a placeholder for the actual annual report.")
    c.drawString(100, 710, "Please replace this file with the actual document.")
    c.save()

os.makedirs('media/reports', exist_ok=True)

years = [
    "2020-21", "2019-20", "2018-19", "2017-18", "2016-17",
    "2015-16", "2014-15", "2013-14", "2012-13", "2011-12",
    "2010-11", "2009-10", "2008-09", "2007-08", "2006-07",
    "2005-06", "2004-05"
]

for year in years:
    filename = f"media/reports/{year}.pdf"
    create_dummy_pdf(filename, year)
    print(f"Created {filename}")
