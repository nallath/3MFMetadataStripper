import argparse
import zipfile
import io
from lxml import etree

namespace = "{http://schemas.microsoft.com/3dmanufacturing/core/2015/02}"


if __name__ == "__main__":

    parser = argparse.ArgumentParser(description='Strip metadata from 3MF files')
    parser.add_argument('source', metavar='source', type=str, nargs='+',
                        help='Source 3mf file')
    parser.add_argument('dest', metavar='dest', type = str, nargs='+', help='Destination of the stripped file')

    args = parser.parse_args()

    new_model_data = ""

    try:
        with zipfile.ZipFile(args.source[0], "r") as source_archive, zipfile.ZipFile(args.dest[0], "w", compression = zipfile.ZIP_DEFLATED) as target_archive:
            model_data = source_archive.open("3D/3dmodel.model").read()
            root = etree.fromstring(model_data)
            

            search = './/{0}metadata'.format(namespace)

            for e in root.findall(search):
                parent = e.getparent()
                try:
                    root.remove(e)
                except:
                    pass

            new_model_data = etree.tostring(root,
                            pretty_print=True,
                            xml_declaration=True,
                            encoding='UTF-8')

            for source_archive_info in source_archive.infolist():
                with source_archive.open(source_archive_info) as source_archive_file:
                    if source_archive_info.filename == "3D/3dmodel.model":
                        content = new_model_data
                    else:
                        content = source_archive_file.read()
                    target_archive.writestr(source_archive_info.filename, content)
    
    except Exception as e:
        print("oh no!", e)

