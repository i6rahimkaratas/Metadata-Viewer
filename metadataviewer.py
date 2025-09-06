import os
from PIL import Image
from PIL.ExifTags import TAGS, GPSTAGS
import datetime

def get_image_metadata(image_path):
    try:
        image = Image.open(image_path)
        
        basic_info = {
            'Dosya Adı': os.path.basename(image_path),
            'Dosya Boyutu': f"{os.path.getsize(image_path) / 1024:.2f} KB",
            'Resim Boyutu': f"{image.width} x {image.height}",
            'Format': image.format,
            'Mod': image.mode
        }
        
        exif_data = {}
        if hasattr(image, '_getexif') and image._getexif() is not None:
            exif = image._getexif()
            
            for tag_id, value in exif.items():
                tag_name = TAGS.get(tag_id, tag_id)
                
                if tag_name == 'GPSInfo':
                    gps_data = {}
                    for gps_tag_id, gps_value in value.items():
                        gps_tag_name = GPSTAGS.get(gps_tag_id, gps_tag_id)
                        gps_data[gps_tag_name] = gps_value
                    exif_data['GPS Bilgileri'] = gps_data
                else:
                    if 'DateTime' in str(tag_name) and isinstance(value, str):
                        try:
                            dt = datetime.datetime.strptime(value, '%Y:%m:%d %H:%M:%S')
                            value = dt.strftime('%d.%m.%Y %H:%M:%S')
                        except:
                            pass
                    
                    exif_data[tag_name] = value
        
        return basic_info, exif_data
        
    except Exception as e:
        return None, f"Hata: {str(e)}"

def print_metadata(basic_info, exif_data):
    print("=" * 60)
    print("RESİM METADATA BİLGİLERİ")
    print("=" * 60)
    
    print("\n📋 TEMEL BİLGİLER:")
    print("-" * 30)
    for key, value in basic_info.items():
        print(f"{key:15}: {value}")
    
    if exif_data and isinstance(exif_data, dict):
        print(f"\n📸 EXIF VERİLERİ ({len(exif_data)} adet):")
        print("-" * 40)
        
        important_tags = ['Make', 'Model', 'DateTime', 'DateTimeOriginal', 
                          'ExposureTime', 'FNumber', 'ISO', 'FocalLength', 
                          'Flash', 'WhiteBalance', 'ColorSpace']
        
        for tag in important_tags:
            if tag in exif_data:
                value = exif_data[tag]
                if tag == 'ExposureTime' and isinstance(value, tuple):
                    value = f"1/{int(1/float(value[0]/value[1]))}" if value[1] != 0 else str(value)
                elif tag == 'FNumber' and isinstance(value, tuple):
                    value = f"f/{value[0]/value[1]:.1f}" if value[1] != 0 else str(value)
                elif tag == 'FocalLength' and isinstance(value, tuple):
                    value = f"{value[0]/value[1]:.1f}mm" if value[1] != 0 else str(value)
                
                print(f"{tag:20}: {value}")
        
        if 'GPS Bilgileri' in exif_data:
            print(f"\n🌍 GPS BİLGİLERİ:")
            print("-" * 20)
            gps_info = exif_data['GPS Bilgileri']
            for gps_key, gps_value in gps_info.items():
                print(f"{gps_key:20}: {gps_value}")
        
        print(f"\n📊 DİĞER EXIF VERİLERİ:")
        print("-" * 25)
        for tag, value in exif_data.items():
            if tag not in important_tags and tag != 'GPS Bilgileri':
                if isinstance(value, (bytes, bytearray)):
                    value = f"<Binary data, {len(value)} bytes>"
                elif isinstance(value, str) and len(value) > 100:
                    value = value[:97] + "..."
                
                print(f"{tag:20}: {value}")
    
    print("\n" + "=" * 60)

def main():
    print("Resim Metadata Okuyucu")
    print("=" * 30)
    
    file_path = input("Resim dosyasının yolunu girin: ").strip().strip('"')
    
    if not os.path.exists(file_path):
        print(f"❌ Hata: '{file_path}' dosyası bulunamadı!")
        return
    
    valid_extensions = ['.jpg', '.jpeg', '.png', '.tiff', '.tif', '.bmp', '.gif']
    if not any(file_path.lower().endswith(ext) for ext in valid_extensions):
        print("⚠️  Uyarı: Bu dosya desteklenen bir resim formatında olmayabilir.")
    
    print("\n📖 Metadata okunuyor...")
    basic_info, exif_data = get_image_metadata(file_path)
    
    if basic_info is None:
        print(f"❌ {exif_data}")
        return
    
    print_metadata(basic_info, exif_data)
    
    save_choice = input("\nSonuçları bir dosyaya kaydetmek ister misiniz? (e/h): ").lower()
    if save_choice == 'e':
        output_file = f"{os.path.splitext(os.path.basename(file_path))[0]}_metadata.txt"
        
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write("RESIM METADATA BİLGİLERİ\n")
            f.write("=" * 60 + "\n\n")
            
            f.write("TEMEL BİLGİLER:\n")
            f.write("-" * 30 + "\n")
            for key, value in basic_info.items():
                f.write(f"{key:15}: {value}\n")
            
            if exif_data and isinstance(exif_data, dict):
                f.write(f"\nEXIF VERİLERİ ({len(exif_data)} adet):\n")
                f.write("-" * 40 + "\n")
                for tag, value in exif_data.items():
                    if isinstance(value, dict):
                        f.write(f"{tag}:\n")
                        for sub_key, sub_value in value.items():
                            f.write(f"  {sub_key}: {sub_value}\n")
                    else:
                        f.write(f"{tag:20}: {value}\n")
        
        print(f"✅ Sonuçlar '{output_file}' dosyasına kaydedildi.")

if __name__ == "__main__":
    main()
