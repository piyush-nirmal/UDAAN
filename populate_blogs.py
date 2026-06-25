import os
from django.utils import timezone
from blood_request.models import Blog, Testimonial

Blog.objects.all().delete()
Testimonial.objects.all().delete()

# Populate Blogs
blog_dir = 'media/blogs'
unique_blogs = set()
if os.path.exists(blog_dir):
    for i, filename in enumerate(os.listdir(blog_dir)):
        # avoiding those duplicated names that end in random strings like _Bkz9AqQ.webp
        if filename.endswith(('.png', '.jpg', '.jpeg', '.webp')) and '_' not in filename[-12:-4]:
            if filename not in unique_blogs:
                unique_blogs.add(filename)
                Blog.objects.create(
                    title=f"Insightful Blog Post {len(unique_blogs)}",
                    content="<p>This is a detailed blog post discussing the impact of our latest initiatives.</p>",
                    description="A brief summary of what this blog discusses.",
                    image=f"blogs/{filename}"
                )
                print(f"Added Blog: {filename}")

# Populate Testimonials
testimonials_data = [
    {
        "author": "Khushal Karnani",
        "role": "Finance Intern (Maharaja Agrasen Institute of Management Studies, Delhi, BCom Hons)",
        "text": "I am writing to share my experience as a Finance Intern at UDAAN Society. It has been a highly enriching and valuable journey for me. During my internship, I worked on four different proposals along with their respective budgets.",
        "detailed_text": "I am writing to share my experience as a Finance Intern at UDAAN Society. It has been a highly enriching and valuable journey for me.\n\nDuring my internship, I worked on four different proposals along with their respective budgets. This experience significantly improved my understanding of budget preparation, cost estimation, and proposal structuring. The practical exposure I gained has contributed greatly to my academic and professional development.\n\nI sincerely appreciate the guidance, support, and opportunity provided to me throughout this internship. The learning environment was very positive and made the entire experience both comfortable and motivating. I truly enjoyed working on the assignments and gained meaningful insights during my time here."
    },
    {
        "author": "Nisarga R Malap",
        "role": "Web Development & IT Intern (Parul Institute of Engineering and Technology)",
        "text": "My internship experience was very valuable and practical. It helped me strengthen my skills in web development, backend integration, database management, UI/UX improvement, chatbot setup, testing, documentation, and teamwork.",
        "detailed_text": "My internship experience was very valuable and practical. It helped me strengthen my skills in web development, backend integration, database management, UI/UX improvement, chatbot setup, testing, documentation, and teamwork. I also gained exposure to real-world project planning, requirement analysis, and knowledge transfer, which improved both my technical confidence and professional communication."
    },
    {
        "author": "Amatullah Jamalee",
        "role": "Media Management Intern (Symbiosis Center for Media and Communication, Tanzania)",
        "text": "My experience working at UDAAN Society as an intern was very nice, during this internship, I learned how a professional workplace functions and improved my communication and teamwork skills.",
        "detailed_text": "My name is Amatullah Jamalee from Tanzania, I am a student of Symbiosis Center for Media and Communication pursuing BBA Media Management.\n\nMy experience working at UDAAN Society as an intern was very nice, during this internship, I learned how a professional workplace functions and improved my communication and teamwork skills.\n\nThis experience helped me gain practical knowledge and confidence."
    },
    {
        "author": "Mohammad Asif",
        "role": "Data Science Intern (ABESIT Group of Institutions, Ghaziabad, B.Tech CSE)",
        "text": "During my internship at UDAAN Society, I had the opportunity to work on the Shiksha Plus dataset related to the Adult Literacy Program. I performed data cleaning, removed duplicate entries, corrected data formats, and organised the data for meaningful analysis.",
        "detailed_text": "I am Mohammad Asif, a B. Tech student specialising in Computer Science and Engineering (Data Science) at ABESIT Group of Institutions, Ghaziabad. I am passionate about data analysis and its potential to drive meaningful change in society, especially in the education and social development sector.\n\nDuring my internship at UDAAN Society, I had the opportunity to work on the Shiksha Plus dataset related to the Adult Literacy Program. I performed data cleaning, removed duplicate entries, corrected data formats, and organised the data for meaningful analysis. I also generated analytical reports, dashboards, and insights that supported program performance evaluation and decision-making. This experience deepened my understanding of how data can empower social organisations to create greater impact."
    }
]

test_dir = 'media/testimonials'
test_images = []
if os.path.exists(test_dir):
    test_images = [f for f in os.listdir(test_dir) if f.endswith(('.png', '.jpg', '.jpeg', '.webp'))]

for i, t_data in enumerate(testimonials_data):
    image_path = f"testimonials/{test_images[i % len(test_images)]}" if test_images else None
    Testimonial.objects.create(
        author=t_data["author"],
        role=t_data["role"],
        text=t_data["text"],
        detailed_text=t_data["detailed_text"],
        image=image_path
    )
    print(f"Added Testimonial: {t_data['author']}")

print("Blogs and Testimonials populated successfully.")
