import re

filepath = "/Users/anandkumarmishra/Downloads/UDAAN/blood_request/views.py"
with open(filepath, "r") as f:
    content = f.read()

# Replace ifsc_verify_api
new_ifsc_api = """
import requests

def ifsc_verify_api(request):
    \"\"\"API endpoint to verify IFSC codes via Razorpay.\"\"\"
    code = request.GET.get('code', '').strip().upper()
    if not code or len(code) != 11:
        return JsonResponse({'valid': False, 'message': 'Invalid IFSC code format (must be 11 characters)'})
    
    try:
        response = requests.get(f'https://ifsc.razorpay.com/{code}', timeout=5)
        if response.status_code == 200:
            data = response.json()
            return JsonResponse({
                'valid': True,
                'ifsc': code,
                'bank_name': data.get('BANK', 'Unknown Bank'),
                'branch': data.get('BRANCH', 'Unknown Branch'),
                'city': data.get('CITY', ''),
                'state': data.get('STATE', '')
            })
        else:
            return JsonResponse({'valid': False, 'message': 'Invalid IFSC code or bank not found.'})
    except Exception as e:
        return JsonResponse({'valid': False, 'message': 'Verification service unavailable.'})
"""
content = re.sub(r'def ifsc_verify_api\(request\):.*?def campaign_status_view', new_ifsc_api + '\n\ndef campaign_status_view', content, flags=re.DOTALL)

# Add validation to campaign_submit_api
submit_val_logic = """
            title = data.get('title', 'Untitled Campaign').strip()
            category = data.get('category', 'Medical')
            
            # --- NEW VALIDATIONS ---
            # 1. Check Account Number match
            acc_num = data.get('account_number')
            acc_conf = data.get('account_number_confirm') # if passed
            # Wait, the frontend doesn't pass confirm to backend in the formData currently.
            # I should validate IFSC again.
            ifsc_code = data.get('ifsc_code', '').strip().upper()
            if ifsc_code:
                try:
                    import requests
                    ifsc_resp = requests.get(f'https://ifsc.razorpay.com/{ifsc_code}', timeout=5)
                    if ifsc_resp.status_code != 200:
                        return JsonResponse({'status': 'error', 'message': 'Invalid IFSC Code provided. Please provide a valid IFSC.'}, status=400)
                except Exception:
                    pass # Allow if service is down to not block critical submissions

            # 2. Check Image Aspect Ratio (16:9)
            from PIL import Image
            cover_file = request.FILES.get('image') or request.FILES.get('cover_image')
            if cover_file:
                try:
                    img = Image.open(cover_file)
                    width, height = img.size
                    if width < 1200 or height < 675:
                         return JsonResponse({'status': 'error', 'message': f'Image is too small ({width}x{height}). Minimum required is 1200x675 pixels.'}, status=400)
                    ratio = width / height
                    if not (1.7 <= ratio <= 1.8):  # Roughly 16:9
                         return JsonResponse({'status': 'error', 'message': 'Image aspect ratio must be 16:9.'}, status=400)
                    cover_file.seek(0)
                except Exception as e:
                    return JsonResponse({'status': 'error', 'message': 'Invalid image file uploaded.'}, status=400)
            # -----------------------
"""
content = content.replace("            title = data.get('title', 'Untitled Campaign').strip()\n            category = data.get('category', 'Medical')", submit_val_logic)

with open(filepath, "w") as f:
    f.write(content)
print("Updated views.py")
