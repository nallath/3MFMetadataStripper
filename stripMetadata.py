import argparse
import zipfile
import xml.etree.ElementTree as ET
import io

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
            from io import StringIO
            found_namespaces = dict([node for _, node in ET.iterparse(StringIO(model_data.decode()), events=['start-ns'])])
            for found_namespace in found_namespaces:
                ET.register_namespace(found_namespace, found_namespaces[found_namespace])


            tree = ET.fromstring(model_data)    
            search = './/{0}metadata'.format(namespace)
            for metadata_item in tree.findall(search):
                try:
                    tree.remove(metadata_item)
                except:
                    pass

            stream = io.BytesIO()
            
            new_tree = ET.ElementTree(tree)
            new_tree.write(stream, encoding = "utf-8", xml_declaration = True)
            new_model_data = stream.getvalue().decode("utf-8")



            for source_archive_info in source_archive.infolist():
                with source_archive.open(source_archive_info) as source_archive_file:
                    if source_archive_info.filename == "3D/3dmodel.model":
                        content = new_model_data
                    else:
                        content = source_archive_file.read()
                    target_archive.writestr(source_archive_info.filename, content)
    
    except Exception as e:
        print("oh no!", e)

