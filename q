[1mdiff --git a/templates/admin/base_site.html b/templates/admin/base_site.html[m
[1mindex 6c8ce7e..c46fa63 100644[m
[1m--- a/templates/admin/base_site.html[m
[1m+++ b/templates/admin/base_site.html[m
[36m@@ -354,8 +354,13 @@[m
     <div class="sidebar-section-title">CONTENT & COMMUNICATIONS</div>[m
     [m
     <a href="{% url 'admin:blood_request_blog_changelist' %}" class="sidebar-link">[m
[32m+[m[32m      <i class="fas fa-blog sidebar-icon"></i>[m
[32m+[m[32m      <span class="sidebar-text">Blogs</span>[m
[32m+[m[32m    </a>[m
[32m+[m
[32m+[m[32m    <a href="{% url 'admin:blood_request_newsclipping_changelist' %}" class="sidebar-link">[m
       <i class="fas fa-newspaper sidebar-icon"></i>[m
[31m-      <span class="sidebar-text">Blogs & News</span>[m
[32m+[m[32m      <span class="sidebar-text">News Clippings</span>[m
     </a>[m
 [m
     <a href="{% url 'admin:blood_request_activity_changelist' %}" class="sidebar-link">[m
