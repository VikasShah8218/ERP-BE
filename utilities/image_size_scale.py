# import cv2
# import os

# def resize_and_save_image(input, output_path: str, max_file_size_kb: int = 10):
#     try:
#         image = cv2.imread(input) if isinstance(input,str) else input
#         if image is None:return False, "Error: Image not found or invalid image format."
#         quality = 90  # Starting JPEG quality
#         scaling_factor = 1.0  # Start with full size
#         success = False
#         while True:
#             new_width = int(image.shape[1] * scaling_factor)
#             new_height = int(image.shape[0] * scaling_factor)
#             resized_image = cv2.resize(image, (new_width, new_height), interpolation=cv2.INTER_AREA)
#             cv2.imwrite(output_path, resized_image, [int(cv2.IMWRITE_JPEG_QUALITY), quality])
#             file_size_kb = os.path.getsize(output_path) / 1024  # Size in KB
#             if file_size_kb <= max_file_size_kb:
#                 success = True
#                 break
#             if quality > 20:
#                 quality -= 10  # Reduce quality
#             elif scaling_factor > 0.1:
#                 scaling_factor -= 0.10  # Reduce size
#             else:
#                 break 
#         if success:
#             message = f"Image resized and saved to {output_path} (Size: {file_size_kb:.2f} KB)"
#             return True, message
#         else:
#             return False, "Error: Could not reduce image size below 50KB."
#     except Exception as e:
#         return False, f"Error while processing the image: {str(e)}"


import os
import cv2

def resize_and_save_image(input, output_path: str, max_file_size_kb: int = 10):
    try:
        image = cv2.imread(input, cv2.IMREAD_UNCHANGED) if isinstance(input, str) else input
        if image is None:
            return False, "Error: Image not found or invalid image format."

        file_extension = os.path.splitext(output_path)[-1].lower()
        quality = 90  # Starting JPEG quality
        scaling_factor = 1.0  # Start with full size
        success = False

        while True:
            new_width = int(image.shape[1] * scaling_factor)
            new_height = int(image.shape[0] * scaling_factor)
            resized_image = cv2.resize(image, (new_width, new_height), interpolation=cv2.INTER_AREA)

            if file_extension == ".png":
                cv2.imwrite(output_path, resized_image, [int(cv2.IMWRITE_PNG_COMPRESSION), 9])
            else:  # Default to JPEG
                cv2.imwrite(output_path, resized_image, [int(cv2.IMWRITE_JPEG_QUALITY), quality])

            file_size_kb = os.path.getsize(output_path) / 1024  # Size in KB

            if file_size_kb <= max_file_size_kb:
                success = True
                break

            if file_extension == ".png":
                if scaling_factor > 0.1:
                    scaling_factor -= 0.10  # Reduce size for PNG
                else:
                    break
            else:  # For JPEG
                if quality > 20:
                    quality -= 10  # Reduce quality
                elif scaling_factor > 0.1:
                    scaling_factor -= 0.10  # Reduce size
                else:
                    break

        if success:
            message = f"Image resized and saved to {output_path} (Size: {file_size_kb:.2f} KB)"
            return True, message
        else:
            return False, f"Error: Could not reduce image size below {max_file_size_kb} KB."
    except Exception as e:
        return False, f"Error while processing the image: {str(e)}"
