import boto3
import os

from PIL import Image, ImageDraw


def process_text_detection(client, document):
    ### Uncomment to analyze a local file ###
    with open(document, 'rb') as image:
        response = client.detect_document_text(Document={'Bytes': image.read()})
        blocks = response['Blocks']
        image = Image.open(image).convert("RGB")

        width, height = image.size
        print ('Detected Document Text')

        # Create image showing bounding box/polygon the detected lines/text
        for block in blocks:
            # Display information about a block returned by text detection
            print('Type: ' + block['BlockType'])
            if block['BlockType'] != 'PAGE':
                print('Detected: ' + block['Text'])
                print('Confidence: ' + "{:.2f}".format(block['Confidence']) + "%")
                print('Id: {}'.format(block['Id']))
            if 'Relationships' in block:
                print('Relationships: {}'.format(block['Relationships']))
                print('Bounding Box: {}'.format(block['Geometry']['BoundingBox']))
                print('Polygon: {}'.format(block['Geometry']['Polygon']))
                print()
            draw=ImageDraw.Draw(image)

            # Draw WORD - Green - start of word, red - end of word
            if block['BlockType'] == "WORD":
                draw.line([(width * block['Geometry']['Polygon'][0]['X'],
                height * block['Geometry']['Polygon'][0]['Y']),
                (width * block['Geometry']['Polygon'][3]['X'],
                height * block['Geometry']['Polygon'][3]['Y'])],fill='green',
                width=2)

            draw.line([(width * block['Geometry']['Polygon'][1]['X'], height * block['Geometry']['Polygon'][1]['Y']),
                       (width * block['Geometry']['Polygon'][2]['X'], height * block['Geometry']['Polygon'][2]['Y'])],
                      fill='red', width=2)

            # Draw box around entire LINE
            if block['BlockType'] == "LINE":
                points=[]
                for polygon in block['Geometry']['Polygon']:
                    points.append((width * polygon['X'], height * polygon['Y']))
                draw.polygon((points), outline='black')

        # Display the image
        image.show()
        return len(blocks)

def main():
    session = boto3.Session(profile_name='kadakareer-dev')
    client = session.client('textract', region_name='us-east-1')
    image_path = "/home/miggy/PycharmProjects/extraTextFromImage/images/"
    images = sorted(os.listdir(image_path))
    for img in images:
        block_count=process_text_detection(client, image_path+img)
        print("Blocks detected: " + str(block_count))

if __name__ == "__main__":
    main()
    