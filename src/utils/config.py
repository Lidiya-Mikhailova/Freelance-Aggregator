import os

from dotenv import load_dotenv

load_dotenv()

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN", "").strip()
TG_CHAT_ID = os.getenv("TG_CHAT_ID", "").strip()

OPENAI_API_KEY = os.getenv("AI_API_KEY") or os.getenv("OPENAI_API_KEY", "").strip()

FLN_OAUTH_TOKEN = os.getenv("FLN_OAUTH_TOKEN", "").strip()
FLN_URL = os.getenv("FLN_URL", "https://www.freelancer.com").strip()

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///data/job_bot.db")

DEBUG_MATCH = os.getenv("DEBUG_MATCH", "0").strip().lower() in {"1", "true", "yes", "on"}

CHECK_INTERVAL_SEC = int(os.getenv("CHECK_INTERVAL_SEC", "300"))
FRESH_WINDOW_SEC = int(os.getenv("FRESH_WINDOW_SEC", str(24 * 60 * 60)))
API_LIMIT = int(os.getenv("API_LIMIT", "200"))
SNIPPET_LIMIT_NOTIFY = int(os.getenv("SNIPPET_LIMIT_NOTIFY", "700"))
SNIPPET_LIMIT_MODEL = int(os.getenv("SNIPPET_LIMIT_MODEL", "900"))

SEARCH_QUERY = os.getenv("SEARCH_QUERY", "").strip()
SEARCH_JOBS = os.getenv("SEARCH_JOBS", "").strip()

SPECIALTIES = {
    "it": {
        "name": "IT",
        "emoji": "💻",
        "children": {
            "it_data_engineer": {
                "name": "Data Engineering",
                "keywords": [
                    "data engineering", "data engineer",
                    "etl", "etl developer", "etl pipeline",
                    "data pipeline", "data warehousing", "data warehouse",
                    "apache spark", "spark", "pyspark", "databricks",
                    "airflow", "apache airflow", "prefect", "dagster",
                    "hadoop", "hive", "hbase", "hdfs",
                    "kafka", "apache kafka", "streaming", "data streaming",
                    "big data", "data lake", "data lakehouse", "delta lake",
                    "sql", "sql developer", "pl/sql", "tsql",
                    "data modeling", "data model", "dimensional modeling",
                    "dbt", "looker", "tableau", "power bi",
                    "snowflake", "bigquery", "redshift", "aws redshift",
                    "python", "python developer", "scala",
                    "data processing", "data ingestion", "data integration",
                    "data migration", "data quality", "data governance",
                    "data catalog", "analytics engineer",
                    "database developer", "database engineer",
                    "data architect", "data analyst",
                    "bi developer", "bi engineer", "business intelligence",
                    "olap", "data mining", "data scraping",
                    "etl automation", "data automation", "data sync",
                    "api integration", "data api", "data extraction",
                    "python scripting", "pandas", "numpy",
                    "data cleaning", "data cleansing", "data wrangling", "data munging",
                ],
                "stop_words": [
                    "logo", "figma", "photoshop", "illustrator", "design",
                    "frontend", "front-end", "react", "vue", "angular", "css", "html",
                    "smm", "seo", "marketing", "copywriting", "translation",
                    "motion", "animation", "3d", "blender", "unity",
                    "game", "mobile", "android", "ios",
                    "wordpress", "shopify", "theme",
                ],
            },
            "it_backend": {
                "name": "Backend Development",
                "keywords": [
                    "backend", "back end", "server", "api", "rest api", "graphql", "endpoint",
                    "node.js", "nodejs", "python", "django", "flask", "fastapi",
                    "java", "spring", "spring boot", "golang", "go lang", "rust", "c++", "c#",
                    "php", "laravel", "symfony", "ruby", "rails", "elixir", "scala",
                    "database", "sql", "postgresql", "mysql", "mariadb", "mongodb", "redis",
                    "docker", "kubernetes", "microservice", "serverless",
                    "aws", "azure", "gcp", "cloud", "devops",
                    "authentication", "authorization", "oauth", "jwt",
                    "websocket", "grpc", "rabbitmq", "kafka",
                    "backend developer", "back-end developer", "server side",
                ],
                "stop_words": [
                    "logo", "figma", "photoshop", "illustrator", "design",
                    "frontend", "front-end", "front end", "react", "vue", "angular", "css", "html",
                    "smm", "seo", "marketing", "copywriting", "translation",
                    "motion", "animation", "3d", "blender", "unity",
                    "video", "photo", "illustration",
                ],
            },
            "it_frontend": {
                "name": "Frontend Development",
                "keywords": [
                    "frontend", "front-end", "front end", "react", "react.js", "reactjs",
                    "vue", "vue.js", "vuejs", "angular", "angular.js", "angularjs",
                    "javascript", "js", "typescript", "ts",
                    "html", "css", "sass", "scss", "less", "tailwind", "bootstrap",
                    "next.js", "nextjs", "nuxt", "nuxt.js", "gatsby", "remix",
                    "webpack", "vite", "redux", "mobx", "jotai",
                    "spa", "pwa", "single page application", "progressive web app",
                    "responsive", "cross-browser", "web development",
                    "frontend developer", "front-end developer", "ui developer",
                    "webpack", "babel", "eslint", "storybook",
                    "styled-components", "css-in-js", "material-ui", "chakra",
                ],
                "stop_words": [
                    "logo", "figma", "photoshop", "illustrator",
                    "backend", "back-end", "back end", "server", "database", "sql",
                    "devops", "docker", "kubernetes", "aws",
                    "smm", "seo", "marketing", "copywriting", "translation",
                    "motion", "animation", "3d", "blender", "unity",
                    "game", "android", "ios", "mobile app",
                ],
            },
            "it_mobile": {
                "name": "Mobile Development",
                "keywords": [
                    "mobile", "android", "ios", "iphone", "ipad", "smartphone",
                    "swift", "swiftui", "uikit", "objective-c", "kotlin", "java android",
                    "flutter", "dart", "react native", "xamarin", "cordova", "ionic",
                    "app development", "mobile app", "native app", "hybrid app",
                    "google play", "app store", "google play store", "apple app store",
                    "mobile developer", "android developer", "ios developer",
                    "push notification", "in-app purchase", "app store connect",
                    "mobile ui", "material design", "cupertino",
                ],
                "stop_words": [
                    "logo", "figma", "photoshop", "illustrator",
                    "backend", "server", "database", "sql", "devops",
                    "smm", "seo", "marketing", "copywriting", "translation",
                    "motion", "animation", "3d", "blender",
                    "frontend", "front-end", "react", "vue", "angular", "css", "html",
                ],
            },
            "it_qa": {
                "name": "QA / Testing",
                "keywords": [
                    "qa", "testing", "quality assurance", "test",
                    "manual testing", "automation testing", "automated testing",
                    "selenium", "cypress", "playwright", "puppeteer",
                    "pytest", "jest", "mocha", "chai", "junit", "testng",
                    "api testing", "postman", "rest assured", "soapui",
                    "performance testing", "load testing", "stress testing", "jmeter", "gatling",
                    "regression", "integration testing", "unit testing", "e2e", "end to end",
                    "test case", "bug report", "bug tracking", "jira",
                    "ci/cd", "jenkins", "gitlab ci", "github actions",
                    "qa engineer", "test engineer", "sdet",
                ],
                "stop_words": [
                    "logo", "figma", "photoshop", "illustrator",
                    "design", "smm", "seo", "marketing", "copywriting", "translation",
                    "motion", "animation", "3d", "blender",
                    "wordpress", "shopify", "theme", "template",
                ],
            },
        },
    },
    "design": {
        "name": "Design",
        "emoji": "🎨",
        "children": {
            "design_ux_ui": {
                "name": "UX/UI Design",
                "keywords": [
                    "ui", "ux", "user interface", "user experience", "ui/ux",
                    "figma", "sketch", "adobe xd", "framer",
                    "prototype", "prototyping", "wireframe", "mockup",
                    "design system", "design token", "component library",
                    "responsive design", "mobile design", "web design", "app design",
                    "landing page", "dashboard design", "saas design",
                    "interaction design", "visual design", "product design",
                    "user research", "usability", "a11y", "accessibility",
                    "ui designer", "ux designer", "product designer",
                    "design thinking", "user flow", "customer journey",
                ],
                "stop_words": [
                    "backend", "frontend", "developer", "programming", "code",
                    "database", "sql", "api", "server", "devops",
                    "testing", "qa", "selenium", "pytest",
                    "copywriting", "translation", "seo", "smm", "ppc",
                    "3d modeling", "blender", "maya", "unity",
                ],
            },
            "design_graphic": {
                "name": "Graphic Design",
                "keywords": [
                    "graphic design", "graphic designer", "visual design",
                    "photoshop", "illustrator", "indesign", "canva", "coreldraw",
                    "branding", "logo", "brand identity", "visual identity",
                    "print design", "brochure", "flyer", "poster", "banner", "business card",
                    "social media post", "social media design",
                    "presentation", "infographic", "pitch deck",
                    "packaging", "label", "merchandise",
                    "advertisement", "ad creative", "display ad",
                    "illustration", "vector", "icon",
                ],
                "stop_words": [
                    "backend", "frontend", "developer", "programming", "code",
                    "database", "sql", "api", "server",
                    "testing", "qa", "selenium",
                    "seo", "smm", "ppc", "copywriting", "translation",
                    "motion graphics", "after effects", "3d modeling", "blender", "maya",
                ],
            },
            "design_motion": {
                "name": "Motion Design",
                "keywords": [
                    "motion", "motion graphics", "motion design",
                    "after effects", "ae", "premiere pro",
                    "animation", "2d animation", "explainer video",
                    "kinetic typography", "lottie", "bodymovin",
                    "video editing", "video production", "video post-production",
                    "vfx", "visual effects", "compositing",
                    "character animation", "rigging 2d",
                    "motion designer", "animator",
                    "title sequence", "lower third", "motion branding",
                ],
                "stop_words": [
                    "backend", "frontend", "developer", "programming", "code",
                    "database", "sql", "api", "server",
                    "testing", "qa",
                    "seo", "smm", "ppc", "copywriting", "translation",
                    "logo", "branding", "print design", "packaging",
                    "3d modeling", "blender", "maya", "zbrush", "unity",
                ],
            },
            "design_3d": {
                "name": "3D Art",
                "keywords": [
                    "3d", "3d modeling", "3d model", "3d modelling",
                    "blender", "maya", "3ds max", "cinema 4d", "c4d", "zbrush",
                    "substance painter", "substance designer", "marmoset",
                    "texture", "texturing", "uv mapping", "baking",
                    "rigging", "skinning", "character rigging",
                    "3d rendering", "render", "vray", "arnold", "cycles", "renderman",
                    "character design", "character modeling", "creature design",
                    "environment", "environment design", "level design",
                    "3d asset", "game asset", "prop modeling",
                    "sculpting", "digital sculpting",
                    "3d animation", "character animation 3d",
                    "unity", "unreal engine", "unreal", "game development",
                    "ar/vr", "augmented reality", "virtual reality",
                ],
                "stop_words": [
                    "backend", "frontend", "developer", "programming", "code",
                    "database", "sql", "api", "server",
                    "testing", "qa",
                    "seo", "smm", "ppc", "copywriting", "translation",
                    "logo", "branding", "print design", "packaging",
                    "video editing", "after effects", "motion graphics",
                ],
            },
        },
    },
    "marketing": {
        "name": "Marketing",
        "emoji": "📈",
        "children": {
            "marketing_seo": {
                "name": "SEO",
                "keywords": [
                    "seo", "search engine optimization", "search engine optimisation",
                    "on-page", "on page", "off-page", "off page",
                    "link building", "backlink", "keyword research",
                    "google analytics", "google search console", "google tag manager",
                    "seo audit", "technical seo", "local seo",
                    "ahrefs", "semrush", "majestic", "moz",
                    "seo strategy", "content seo", "seo optimization",
                    "seo specialist", "seo manager",
                ],
                "stop_words": [
                    "backend", "frontend", "developer", "programming", "code",
                    "database", "sql", "api", "server",
                    "design", "figma", "photoshop", "illustrator",
                    "3d", "animation", "motion",
                    "translation", "transcription",
                ],
            },
            "marketing_smm": {
                "name": "SMM",
                "keywords": [
                    "smm", "social media", "social media marketing",
                    "instagram", "facebook", "tiktok", "twitter", "x ", "linkedin",
                    "telegram channel", "youtube",
                    "content plan", "content strategy", "content calendar",
                    "community management", "community manager",
                    "social media manager", "smm manager",
                    "influencer", "influencer marketing",
                    "social media strategy", "engagement",
                    "social media post", "social media content",
                    "tiktok content", "reels", "shorts",
                ],
                "stop_words": [
                    "backend", "frontend", "developer", "programming", "code",
                    "database", "sql", "api", "server",
                    "design", "figma", "photoshop", "illustrator",
                    "3d", "animation", "motion",
                    "translation", "transcription",
                    "seo technical", "link building",
                ],
            },
            "marketing_ppc": {
                "name": "PPC / Advertising",
                "keywords": [
                    "ppc", "google ads", "google adwords", "facebook ads", "meta ads",
                    "advertising", "paid traffic", "paid media",
                    "conversion", "cpa", "cpc", "cpm", "roi", "roas",
                    "google analytics", "google tag manager", "google optimize",
                    "campaign management", "ad campaign",
                    "remarketing", "retargeting",
                    "a/b testing", "split testing",
                    "landing page", "ad creative", "ad copy",
                    "ppc specialist", "media buyer", "performance marketing",
                ],
                "stop_words": [
                    "backend", "frontend", "developer", "programming", "code",
                    "database", "sql", "api", "server",
                    "design", "figma", "photoshop", "illustrator",
                    "3d", "animation", "motion",
                    "translation", "transcription",
                    "seo", "link building", "keyword research",
                ],
            },
            "marketing_email": {
                "name": "Email Marketing",
                "keywords": [
                    "email marketing", "email campaign", "email automation",
                    "newsletter", "mailchimp", "sendgrid", "mailgun", "brevo", "sendinblue",
                    "email design", "email template", "html email",
                    "drip campaign", "drip email", "automation workflow",
                    "email list", "lead nurturing", "lead generation",
                    "convertkit", "activecampaign", "getresponse", "aweber",
                    "email copy", "subject line", "cta",
                    "email marketing manager", "email specialist",
                    "a/b testing email", "email analytics",
                ],
                "stop_words": [
                    "backend", "frontend", "developer", "programming", "code",
                    "database", "sql", "api", "server",
                    "design", "figma", "photoshop", "illustrator",
                    "3d", "animation", "motion",
                    "seo", "smm", "ppc",
                    "translation", "transcription",
                ],
            },
        },
    },
    "writing": {
        "name": "Writing & Translation",
        "emoji": "✍️",
        "children": {
            "writing_copywriting": {
                "name": "Copywriting",
                "keywords": [
                    "copywriting", "copywriter", "copy write", "copy writer",
                    "content writing", "content writer",
                    "blog post", "article writing", "article writer",
                    "web content", "website content",
                    "seo content", "seo writing",
                    "sales copy", "landing page copy", "landing page text",
                    "email copy", "newsletter copy",
                    "product description", "product copy",
                    "ad copy", "advertising copy",
                    "script writing", "video script",
                    "storytelling", "brand copy",
                    "copy editor", "proofreading",
                ],
                "stop_words": [
                    "backend", "frontend", "developer", "programming", "code",
                    "database", "sql", "api", "server",
                    "design", "figma", "photoshop", "illustrator",
                    "3d", "animation", "motion",
                    "smm", "ppc", "seo audit", "link building",
                ],
            },
            "writing_technical": {
                "name": "Technical Writing",
                "keywords": [
                    "technical writing", "technical writer",
                    "documentation", "api documentation", "developer documentation",
                    "user manual", "user guide", "instruction manual",
                    "knowledge base", "kb article",
                    "white paper", "whitepaper", "case study",
                    "specification", "tech spec", "software documentation",
                    "help center", "help article", "faq",
                    "release notes", "changelog",
                    "technical content", "developer guide",
                    "how-to guide", "tutorial",
                ],
                "stop_words": [
                    "design", "figma", "photoshop", "illustrator",
                    "3d", "animation", "motion",
                    "smm", "ppc", "seo",
                    "logo", "branding", "illustration",
                ],
            },
            "writing_translation": {
                "name": "Translation",
                "keywords": [
                    "translation", "translate", "translator",
                    "localization", "l10n", "i18n", "internationalization",
                    "interpreter", "interpretation",
                    "document translation", "website translation",
                    "english to russian", "russian to english",
                    "english to spanish", "spanish to english",
                    "bilingual", "multilingual",
                    "proofreading", "transcreation",
                    "subtitle", "voiceover",
                    "medical translation", "technical translation", "legal translation",
                ],
                "stop_words": [
                    "backend", "frontend", "developer", "programming", "code",
                    "database", "sql", "api", "server",
                    "design", "figma", "photoshop",
                    "3d", "animation", "motion",
                    "smm", "ppc",
                    "copywriting", "content writing",
                ],
            },
        },
    },
    "admin": {
        "name": "Admin & VA",
        "emoji": "📋",
        "children": {
            "admin_va": {
                "name": "Virtual Assistant",
                "keywords": [
                    "virtual assistant", "va", "remote assistant",
                    "personal assistant", "executive assistant",
                    "administrative support", "admin assistant",
                    "calendar management", "email management",
                    "scheduling", "appointment setting",
                    "travel booking", "research",
                    "data entry", "customer support",
                    "virtual assistant services",
                    "online assistant", "administrative virtual assistant",
                ],
                "stop_words": [
                    "backend", "frontend", "developer", "programming", "code",
                    "database", "sql", "api", "server",
                    "design", "figma", "photoshop", "illustrator",
                    "3d", "animation", "motion",
                    "seo", "smm", "ppc",
                    "testing", "qa", "selenium",
                ],
            },
            "admin_data_entry": {
                "name": "Data Entry",
                "keywords": [
                    "data entry", "data input", "data capture",
                    "copy paste", "typing", "type",
                    "excel", "spreadsheet", "google sheets",
                    "database entry", "form filling",
                    "data cleaning", "data cleansing", "data processing",
                    "data extraction", "data conversion",
                    "data entry operator", "data entry clerk",
                    "pdf to excel", "pdf to word",
                    "web research", "internet research",
                ],
                "stop_words": [
                    "backend", "frontend", "developer", "programming", "code",
                    "api", "server", "design", "figma", "photoshop",
                    "3d", "animation", "motion",
                    "seo", "smm", "ppc",
                    "testing", "qa",
                ],
            },
            "admin_support": {
                "name": "Customer Support",
                "keywords": [
                    "customer support", "customer service", "support agent",
                    "help desk", "helpdesk", "ticket system",
                    "live chat", "chat support",
                    "technical support", "tech support",
                    "email support", "phone support",
                    "customer success", "client support",
                    "support specialist", "support representative",
                    "crm", "zendesk", "freshdesk", "intercom",
                    "chatbot", "conversational ai",
                ],
                "stop_words": [
                    "backend", "frontend", "developer", "programming", "code",
                    "database", "sql", "api", "server",
                    "design", "figma", "photoshop", "illustrator",
                    "3d", "animation", "motion",
                    "seo", "smm", "ppc",
                    "copywriting", "translation",
                ],
            },
        },
    },
}

SPECIALTY_FLAT = {}
for cat_key, cat in SPECIALTIES.items():
    for child_key, child in cat["children"].items():
        SPECIALTY_FLAT[child_key] = {**child, "category_key": cat_key}

SPECIALTY_CHOICES = {k: v["name"] for k, v in SPECIALTY_FLAT.items()}

KEYWORDS = SPECIALTY_FLAT["admin_data_entry"]["keywords"]
STOP_WORDS = SPECIALTY_FLAT["admin_data_entry"]["stop_words"]
