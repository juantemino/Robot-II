from robocorp.tasks import task
from robocorp import browser
from RPA.HTTP import HTTP
from RPA.Tables import Tables
from RPA.PDF import PDF
from RPA.Archive import Archive

@task
def order_robots_from_RobotSpareBin():
    """
    Orders robots from RobotSpareBin Industries Inc.
    Saves the order HTML receipt as a PDF file.
    Saves the screenshot of the ordered robot.
    Embeds the screenshot of the robot to the PDF receipt.
    Creates ZIP archive of the receipts and the images.
    """
    browser.configure(
        slowmo=1000,
    )
    open_robot_order_website()
    orders = get_orders()
    for row in orders:
        fill_the_form(row)
    archive_receipts()
    
def open_robot_order_website():
    """Navegar a la página web aportada"""
    browser.goto("https://robotsparebinindustries.com/#/robot-order")
def get_orders():
    """Descargar el archivo CSV de pedidos"""
    http = HTTP()
    library = Tables()
    http.download(url="https://robotsparebinindustries.com/orders.csv", overwrite=True)
    orders = library.read_table_from_csv("orders.csv", columns=["Order number","Head","Body","Legs","Address"])
    return orders
def close_annoying_modal():
    page = browser.page()
    page.click(selector="#root > div > div.modal > div > div > div > div > div > button.btn.btn-dark")
def fill_the_form(fila_pedido):
    close_annoying_modal()
    page = browser.page()
    page.select_option('#head',fila_pedido["Head"])
    page.click('#id-body-'+fila_pedido["Body"])
    page.fill(selector='.form-control',value=fila_pedido['Legs'])
    page.fill('#address',fila_pedido['Address'])

    page.click('#preview')
    page.click('#order')

    while page.is_visible('//*[@class="alert alert-danger"]'):
        page.click('#order')
    path_pdf = store_receipt_as_pdf(fila_pedido['Order number'])
    path_screenshot = screenshot_robot(fila_pedido['Order number'])
    if page.is_visible('#receipt > h3'):
        page.click('#order-another')
    embed_screenshot_to_receipt(path_screenshot, path_pdf,fila_pedido['Order number'])

def store_receipt_as_pdf(order_number):
    page = browser.page()
    receipt = page.locator('#receipt').inner_html()

    pdf = PDF()
    path = 'output/'+order_number+'.pdf'
    pdf.html_to_pdf(receipt,path)
    return path
def screenshot_robot(order_number):
    page = browser.page()

    path = 'output/'+order_number+'.png'
    page.screenshot(path=path)
    return path
def embed_screenshot_to_receipt(screenshot, pdf_file, order_number):
    pdf = PDF()
    lista_archivos = [pdf_file, screenshot]
    path = "output/DocumentosCombinados/combinacion_pedido_"+order_number+'.pdf'
    pdf.add_files_to_pdf(files=lista_archivos,target_document=path)
def archive_receipts():
    fs = Archive()
    directorio = "output/DocumentosCombinados/"
    nombre_zip = "output/zip_documentos.zip"
    fs.archive_folder_with_zip(directorio,nombre_zip)