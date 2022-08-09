from ptext.pdf.document import Document
from ptext.pdf.page.page import Page
from ptext.pdf.pdf import PDF
from ptext.pdf.canvas.layout.paragraph import Paragraph
from ptext.pdf.canvas.layout.page_layout import SingleColumnLayout
from ptext.io.read.types import Decimal


@property
def create_cart(ingredients, name):
    final_list = {}
    document = Document()
    page = Page()
    layout = SingleColumnLayout(page)
    for ingredient in ingredients:
        ing = ingredient[0]
        if ing not in final_list:
            final_list[ing] = {
                'measurement_unit': ingredient[1],
                'amount': ingredient[2]
            }
        else:
            final_list[ing]['amount'] += ingredient[2]

    layout.add(Paragraph(final_list), font_size=Decimal(14), font='Helvetica')

    with open(f'{name}.pdf', 'wb') as pdf_file_handle:
        PDF.dumps(pdf_file_handle, document)
