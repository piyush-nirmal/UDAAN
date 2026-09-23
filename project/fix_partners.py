import re

with open('templates/our_partners.html', 'r', encoding='utf-8') as f:
    content = f.read()

# Replace the content of all card-grid divs with the generated images
pattern = re.compile(r'<div class=\"card-grid\">.*?</div>\s*</section>', re.DOTALL)

replacement = '''<div class=\"card-grid\">
        <div class=\"partner-card\">
            <img src=\"{% static 'images/partner_amu.png' %}\" alt=\"AMU\">
            <h3>Aligarh Muslim University</h3>
            <p>Aligarh</p>
        </div>
        <div class=\"partner-card\">
            <img src=\"{% static 'images/partner_unicef.png' %}\" alt=\"UNICEF\">
            <h3>UNICEF</h3>
            <p>Global</p>
        </div>
        <div class=\"partner-card\">
            <img src=\"{% static 'images/partner_lic.png' %}\" alt=\"LIC\">
            <h3>LIC of India</h3>
            <p>India</p>
        </div>
    </div>
</section>'''

new_content = pattern.sub(replacement, content)

with open('templates/our_partners.html', 'w', encoding='utf-8') as f:
    f.write(new_content)

print('Updated our_partners.html')
