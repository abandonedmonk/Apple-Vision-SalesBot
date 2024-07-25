import textwrap
import requests
from bs4 import BeautifulSoup
from fpdf import FPDF


def extract_from_url(url):
    response = requests.get(url)
    if response.status_code != 200:
        print(f"Failed to fetch {url}")
        return None

    html_content = response.content
    soup = BeautifulSoup(html_content, 'html.parser')

    extracted_data = ""

    # Extract the main title
    main_title = soup.find('h1').get_text(
        strip=True) if soup.find('h1') else "No title found"
    extracted_data += f"Main Title: {main_title}\n\n"

    # Extract all paragraph texts
    paragraphs = soup.find_all('p')
    for para in paragraphs:
        extracted_data += f"Paragraph: {para.get_text(strip=True)}\n\n"

    # Extract all subheadings and their associated texts
    subheads = soup.find_all('div', class_='Subhead')
    for subhead in subheads:
        subhead_title = subhead.find('h2', class_='Name').get_text(
            strip=True) if subhead.find('h2', class_='Name') else "No subheading found"
        subhead_text = subhead.find('p').get_text(
            strip=True) if subhead.find('p') else "No subheading text found"
        extracted_data += f"Subheading: {subhead_title}\n"
        extracted_data += f"Subheading Text: {subhead_text}\n\n"

    # Extract all 'See also' links
    see_also_section = soup.find('div', class_='LinkUniversal')
    if see_also_section:
        see_also_links = see_also_section.find_all('a')
        for link in see_also_links:
            link_text = link.get_text(strip=True)
            link_url = link['href']
            extracted_data += f"See Also Link Text: {link_text}\n"
            extracted_data += f"See Also Link URL: {link_url}\n\n"
    print(extracted_data)
    return extracted_data


def text_to_pdf(text, filename):
    a4_width_mm = 210
    pt_to_mm = 0.35
    fontsize_pt = 10
    fontsize_mm = fontsize_pt * pt_to_mm
    margin_bottom_mm = 10
    character_width_mm = 7 * pt_to_mm
    width_text = a4_width_mm / character_width_mm

    pdf = FPDF(orientation='P', unit='mm', format='A4')
    pdf.set_auto_page_break(True, margin=margin_bottom_mm)
    pdf.add_page()
    pdf.set_font(family='Courier', size=fontsize_pt)
    splitted = text.split('\n')

    for line in splitted:
        lines = textwrap.wrap(line, width_text)

        if len(lines) == 0:
            pdf.ln()

        for wrap in lines:
            pdf.cell(0, fontsize_mm, wrap, ln=1)

    pdf.output(filename, 'F')


# List of URLs to extract data from
urls = [
    "https://www.apple.com/apple-vision-pro/",
    "https://support.apple.com/en-in/guide/apple-vision-pro/tan39b6bab8f/1.0/visionos/1.0",
    "https://support.apple.com/en-in/guide/apple-vision-pro/tan440238696/1.0/visionos/1.0",
    "https://support.apple.com/en-in/guide/apple-vision-pro/deve0c57808f/1.0/visionos/1.0",
    "https://support.apple.com/en-in/guide/apple-vision-pro/tanb58c3cfaf/1.0/visionos/1.0",
    "https://support.apple.com/en-in/guide/apple-vision-pro/tand3233e05b/1.0/visionos/1.0"
]


# pdf = PDF()
# pdf.add_page()

for url in urls:
    print(f"Extracting data from: {url}")
    extracted_text = extract_from_url(url)
    # if extracted_text:
    #     pdf.chapter_title(f"Extracted data from: {url}")
    #     pdf.chapter_body(extracted_text)
    # print("\n" + "="*50 + "\n")
    # output_filename = 'extracted_data.pdf'
    # text_to_pdf(extracted_text, output_filename)

    text_file = open("Output.txt", "a", encoding="utf-8")

    text_file.write(extracted_text)

    text_file.close()

# Save the extracted data to a PDF file
# pdf.output("extracted_data.pdf")

# print("Data has been saved to extracted_data.pdf")
