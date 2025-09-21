from django.core.management.base import BaseCommand
from django.utils.translation import activate
from products.models import Category, Product
from pages.models import SiteSettings


class Command(BaseCommand):
    help = 'Populate sample data with translations'

    def handle(self, *args, **options):
        self.stdout.write('Creating sample data with translations...')
        
        # Create site settings with translations
        self.create_site_settings()
        
        # Create categories with translations
        categories = self.create_categories()
        
        # Create products with translations
        self.create_products(categories)
        
        self.stdout.write(self.style.SUCCESS('Sample data created successfully!'))

    def create_site_settings(self):
        """Create site settings with translations"""
        settings, created = SiteSettings.objects.get_or_create(pk=1)
        
        # English (default)
        activate('en')
        settings.site_name = 'Green Houses CBD'
        settings.tagline = 'Premium Natural Medical Products'
        settings.address = 'Paris, France'
        settings.business_hours = 'Mon-Fri: 9:00-18:00\nSat: 10:00-16:00\nSun: Closed'
        settings.about_text = 'We specialize in premium natural medical products derived from organic sources.'
        settings.save()
        
        # French
        activate('fr')
        settings.site_name = 'Magasin GreenMed'
        settings.tagline = 'Produits Médicaux Naturels Premium'
        settings.address = 'Paris, France'
        settings.business_hours = 'Lun-Ven: 9h00-18h00\nSam: 10h00-16h00\nDim: Fermé'
        settings.about_text = 'Nous nous spécialisons dans les produits médicaux naturels premium dérivés de sources biologiques.'
        settings.save()
        
        # German
        activate('de')
        settings.site_name = 'GreenMed Geschäft'
        settings.tagline = 'Premium Natürliche Medizinische Produkte'
        settings.address = 'Paris, Frankreich'
        settings.business_hours = 'Mo-Fr: 9:00-18:00\nSa: 10:00-16:00\nSo: Geschlossen'
        settings.about_text = 'Wir spezialisieren uns auf premium natürliche medizinische Produkte aus biologischen Quellen.'
        settings.save()
        
        # Spanish
        activate('es')
        settings.site_name = 'Tienda GreenMed'
        settings.tagline = 'Productos Médicos Naturales Premium'
        settings.address = 'París, Francia'
        settings.business_hours = 'Lun-Vie: 9:00-18:00\nSáb: 10:00-16:00\nDom: Cerrado'
        settings.about_text = 'Nos especializamos en productos médicos naturales premium derivados de fuentes orgánicas.'
        settings.save()
        
        # Italian
        activate('it')
        settings.site_name = 'Negozio GreenMed'
        settings.tagline = 'Prodotti Medici Naturali Premium'
        settings.address = 'Parigi, Francia'
        settings.business_hours = 'Lun-Ven: 9:00-18:00\nSab: 10:00-16:00\nDom: Chiuso'
        settings.about_text = 'Ci specializziamo in prodotti medici naturali premium derivati da fonti biologiche.'
        settings.save()
        
        activate('en')  # Reset to English
        self.stdout.write('Site settings created with translations')

    def create_categories(self):
        """Create categories with translations"""
        categories_data = [
            {
                'slug': 'cbd-products',
                'translations': {
                    'en': {'name': 'CBD Products', 'description': 'High-quality CBD products for wellness and health'},
                    'fr': {'name': 'Produits CBD', 'description': 'Produits CBD de haute qualité pour le bien-être et la santé'},
                    'de': {'name': 'CBD-Produkte', 'description': 'Hochwertige CBD-Produkte für Wellness und Gesundheit'},
                    'es': {'name': 'Productos CBD', 'description': 'Productos CBD de alta calidad para bienestar y salud'},
                    'it': {'name': 'Prodotti CBD', 'description': 'Prodotti CBD di alta qualità per benessere e salute'},
                    'da': {'name': 'CBD Produkter', 'description': 'Højkvalitets CBD produkter til wellness og sundhed'},
                    'fi': {'name': 'CBD Tuotteet', 'description': 'Korkealaatuisia CBD tuotteita hyvinvointiin ja terveyteen'},
                    'hu': {'name': 'CBD Termékek', 'description': 'Magas minőségű CBD termékek wellness és egészség céljából'},
                    'no': {'name': 'CBD Produkter', 'description': 'Høykvalitets CBD produkter for velvære og helse'},
                    'ga': {'name': 'Táirgí CBD', 'description': 'Táirgí CBD ardchaighdeáin le haghaidh folláine agus sláinte'},
                    'sv': {'name': 'CBD Produkter', 'description': 'Högkvalitativa CBD produkter för välbefinnande och hälsa'}
                }
            },
            {
                'slug': 'herbal-remedies',
                'translations': {
                    'en': {'name': 'Herbal Remedies', 'description': 'Traditional herbal medicines and natural remedies'},
                    'fr': {'name': 'Remèdes à base de plantes', 'description': 'Médecines traditionnelles à base de plantes et remèdes naturels'},
                    'de': {'name': 'Kräuterheilmittel', 'description': 'Traditionelle Kräutermedizin und natürliche Heilmittel'},
                    'es': {'name': 'Remedios Herbales', 'description': 'Medicinas herbales tradicionales y remedios naturales'},
                    'it': {'name': 'Rimedi Erboristici', 'description': 'Medicine erboristiche tradizionali e rimedi naturali'},
                    'da': {'name': 'Urtemedicin', 'description': 'Traditionel urtemedicin og naturlige remedier'},
                    'fi': {'name': 'Yrttilääkkeet', 'description': 'Perinteiset yrttilääkkeet ja luonnolliset lääkkeet'},
                    'hu': {'name': 'Gyógynövényes Szerek', 'description': 'Hagyományos gyógynövényes gyógyszerek és természetes szerek'},
                    'no': {'name': 'Urteremedier', 'description': 'Tradisjonelle urtemedisin og naturlige remedier'},
                    'ga': {'name': 'Leigheasanna Luibheanna', 'description': 'Leigheas traidisiúnta luibheanna agus leigheasanna nádúrtha'},
                    'sv': {'name': 'Örtmedicin', 'description': 'Traditionell örtmedicin och naturliga botemedel'}
                }
            },
            {
                'slug': 'organic-supplements',
                'translations': {
                    'en': {'name': 'Organic Supplements', 'description': 'Certified organic dietary supplements and vitamins'},
                    'fr': {'name': 'Suppléments Biologiques', 'description': 'Suppléments alimentaires et vitamines biologiques certifiés'},
                    'de': {'name': 'Bio-Nahrungsergänzungsmittel', 'description': 'Zertifizierte biologische Nahrungsergänzungsmittel und Vitamine'},
                    'es': {'name': 'Suplementos Orgánicos', 'description': 'Suplementos dietéticos y vitaminas orgánicas certificadas'},
                    'it': {'name': 'Integratori Biologici', 'description': 'Integratori alimentari e vitamine biologiche certificate'},
                    'da': {'name': 'Økologiske Kosttilskud', 'description': 'Certificerede økologiske kosttilskud og vitaminer'},
                    'fi': {'name': 'Luomu Ravintolisät', 'description': 'Sertifioidut luomu ravintolisät ja vitamiinit'},
                    'hu': {'name': 'Bio Kiegészítők', 'description': 'Tanúsított bio étrend-kiegészítők és vitaminok'},
                    'no': {'name': 'Økologiske Kosttilskudd', 'description': 'Sertifiserte økologiske kosttilskudd og vitaminer'},
                    'ga': {'name': 'Forlíontaí Orgánacha', 'description': 'Forlíontaí bia agus vitimíní orgánacha deimhnithe'},
                    'sv': {'name': 'Ekologiska Kosttillskott', 'description': 'Certifierade ekologiska kosttillskott och vitaminer'}
                }
            }
        ]
        
        categories = []
        for cat_data in categories_data:
            category, created = Category.objects.get_or_create(slug=cat_data['slug'])
            
            for lang_code, translation in cat_data['translations'].items():
                activate(lang_code)
                category.name = translation['name']
                category.description = translation['description']
                category.save()
            
            categories.append(category)
            activate('en')  # Reset to English
        
        self.stdout.write(f'Created {len(categories)} categories with translations')
        return categories

    def create_products(self, categories):
        """Create products with translations"""
        products_data = [
            {
                'slug': 'premium-cbd-oil',
                'category': categories[0],  # CBD Products
                'price': '49.99',
                'translations': {
                    'en': {
                        'name': 'Premium CBD Oil',
                        'description': 'High-quality full-spectrum CBD oil extracted from organic hemp',
                        'composition': 'Organic hemp extract, MCT oil, natural flavoring',
                        'usage_instructions': 'Take 1-2 drops under tongue twice daily',
                        'creation_method': 'CO2 extraction from organic hemp plants',
                        'benefits': 'May help with relaxation, sleep quality, and general wellness'
                    },
                    'fr': {
                        'name': 'Huile CBD Premium',
                        'description': 'Huile CBD à spectre complet de haute qualité extraite du chanvre biologique',
                        'composition': 'Extrait de chanvre biologique, huile MCT, arôme naturel',
                        'usage_instructions': 'Prendre 1-2 gouttes sous la langue deux fois par jour',
                        'creation_method': 'Extraction CO2 à partir de plants de chanvre biologiques',
                        'benefits': 'Peut aider à la relaxation, à la qualité du sommeil et au bien-être général'
                    },
                    'de': {
                        'name': 'Premium CBD Öl',
                        'description': 'Hochwertiges Vollspektrum-CBD-Öl aus biologischem Hanf extrahiert',
                        'composition': 'Bio-Hanfextrakt, MCT-Öl, natürliche Aromen',
                        'usage_instructions': '1-2 Tropfen zweimal täglich unter die Zunge nehmen',
                        'creation_method': 'CO2-Extraktion aus biologischen Hanfpflanzen',
                        'benefits': 'Kann bei Entspannung, Schlafqualität und allgemeinem Wohlbefinden helfen'
                    },
                    'es': {
                        'name': 'Aceite CBD Premium',
                        'description': 'Aceite CBD de espectro completo de alta calidad extraído de cáñamo orgánico',
                        'composition': 'Extracto de cáñamo orgánico, aceite MCT, saborizante natural',
                        'usage_instructions': 'Tomar 1-2 gotas bajo la lengua dos veces al día',
                        'creation_method': 'Extracción CO2 de plantas de cáñamo orgánicas',
                        'benefits': 'Puede ayudar con la relajación, calidad del sueño y bienestar general'
                    },
                    'it': {
                        'name': 'Olio CBD Premium',
                        'description': 'Olio CBD a spettro completo di alta qualità estratto da canapa biologica',
                        'composition': 'Estratto di canapa biologica, olio MCT, aromatizzante naturale',
                        'usage_instructions': 'Assumere 1-2 gocce sotto la lingua due volte al giorno',
                        'creation_method': 'Estrazione CO2 da piante di canapa biologiche',
                        'benefits': 'Può aiutare con rilassamento, qualità del sonno e benessere generale'
                    },
                    'da': {
                        'name': 'Premium CBD Olie',
                        'description': 'Højkvalitets fuldspektrum CBD olie udvundet fra økologisk hamp',
                        'composition': 'Økologisk hampekstrakt, MCT olie, naturlig smag',
                        'usage_instructions': 'Tag 1-2 dråber under tungen to gange dagligt',
                        'creation_method': 'CO2 ekstraktion fra økologiske hampeplanter',
                        'benefits': 'Kan hjælpe med afslapning, søvnkvalitet og generel velvære'
                    },
                    'fi': {
                        'name': 'Premium CBD Öljy',
                        'description': 'Korkealaatuinen täysspektri CBD öljy luomuhampusta',
                        'composition': 'Luomu hamppu uute, MCT öljy, luonnollinen maku',
                        'usage_instructions': 'Ota 1-2 tippaa kielen alle kahdesti päivässä',
                        'creation_method': 'CO2 uutto luomu hamppu kasveista',
                        'benefits': 'Voi auttaa rentoutumisessa, unen laadussa ja yleisessä hyvinvoinnissa'
                    },
                    'hu': {
                        'name': 'Prémium CBD Olaj',
                        'description': 'Magas minőségű teljes spektrumú CBD olaj bio kenderből kivonva',
                        'composition': 'Bio kender kivonat, MCT olaj, természetes ízesítő',
                        'usage_instructions': 'Vegyen be 1-2 cseppet a nyelv alá naponta kétszer',
                        'creation_method': 'CO2 kivonás bio kender növényekből',
                        'benefits': 'Segíthet a relaxációban, az alvás minőségében és az általános jóllétben'
                    },
                    'no': {
                        'name': 'Premium CBD Olje',
                        'description': 'Høykvalitets fullspektrum CBD olje utvunnet fra økologisk hamp',
                        'composition': 'Økologisk hampekstrakt, MCT olje, naturlig smak',
                        'usage_instructions': 'Ta 1-2 dråper under tungen to ganger daglig',
                        'creation_method': 'CO2 ekstraksjon fra økologiske hampplanter',
                        'benefits': 'Kan hjelpe med avslapning, søvnkvalitet og generell velvære'
                    },
                    'ga': {
                        'name': 'Ola CBD Préimhe',
                        'description': 'Ola CBD speictream iomlán ardchaighdeáin arna bhaint as cnáib orgánach',
                        'composition': 'Sliocht cnáibe orgánaí, ola MCT, blasú nádúrtha',
                        'usage_instructions': 'Glac 1-2 braon faoin teanga faoi dhó sa lá',
                        'creation_method': 'Eastóscadh CO2 ó phlandaí cnáibe orgánacha',
                        'benefits': 'D\'fhéadfadh sé cabhrú le scíth, cáilíocht codlata agus folláine ginearálta'
                    },
                    'sv': {
                        'name': 'Premium CBD Olja',
                        'description': 'Högkvalitativ fullspektrum CBD olja utvunnen från ekologisk hampa',
                        'composition': 'Ekologiskt hampextrakt, MCT olja, naturlig smak',
                        'usage_instructions': 'Ta 1-2 droppar under tungan två gånger dagligen',
                        'creation_method': 'CO2 extraktion från ekologiska hampväxter',
                        'benefits': 'Kan hjälpa med avslappning, sömnkvalitet och allmänt välbefinnande'
                    }
                }
            },
            {
                'slug': 'chamomile-tea',
                'category': categories[1],  # Herbal Remedies
                'price': '12.99',
                'translations': {
                    'en': {
                        'name': 'Organic Chamomile Tea',
                        'description': 'Soothing chamomile tea made from organic flowers',
                        'composition': '100% organic chamomile flowers',
                        'usage_instructions': 'Steep 1 teaspoon in hot water for 5-7 minutes',
                        'creation_method': 'Carefully dried organic chamomile flowers',
                        'benefits': 'Promotes relaxation and may improve sleep quality'
                    },
                    'fr': {
                        'name': 'Thé à la Camomille Biologique',
                        'description': 'Thé à la camomille apaisant fait à partir de fleurs biologiques',
                        'composition': '100% fleurs de camomille biologiques',
                        'usage_instructions': 'Infuser 1 cuillère à café dans de l\'eau chaude pendant 5-7 minutes',
                        'creation_method': 'Fleurs de camomille biologiques soigneusement séchées',
                        'benefits': 'Favorise la relaxation et peut améliorer la qualité du sommeil'
                    },
                    'de': {
                        'name': 'Bio-Kamillentee',
                        'description': 'Beruhigender Kamillentee aus biologischen Blüten',
                        'composition': '100% biologische Kamillenblüten',
                        'usage_instructions': '1 Teelöffel in heißem Wasser 5-7 Minuten ziehen lassen',
                        'creation_method': 'Sorgfältig getrocknete biologische Kamillenblüten',
                        'benefits': 'Fördert Entspannung und kann die Schlafqualität verbessern'
                    },
                    'es': {
                        'name': 'Té de Manzanilla Orgánica',
                        'description': 'Té de manzanilla calmante hecho de flores orgánicas',
                        'composition': '100% flores de manzanilla orgánicas',
                        'usage_instructions': 'Remojar 1 cucharadita en agua caliente por 5-7 minutos',
                        'creation_method': 'Flores de manzanilla orgánicas cuidadosamente secadas',
                        'benefits': 'Promueve la relajación y puede mejorar la calidad del sueño'
                    },
                    'it': {
                        'name': 'Tè alla Camomilla Biologica',
                        'description': 'Tè alla camomilla rilassante fatto da fiori biologici',
                        'composition': '100% fiori di camomilla biologici',
                        'usage_instructions': 'Lasciare in infusione 1 cucchiaino in acqua calda per 5-7 minuti',
                        'creation_method': 'Fiori di camomilla biologici accuratamente essiccati',
                        'benefits': 'Promuove il rilassamento e può migliorare la qualità del sonno'
                    }
                }
            },
            {
                'slug': 'vitamin-d3-supplement',
                'category': categories[2],  # Organic Supplements
                'price': '24.99',
                'translations': {
                    'en': {
                        'name': 'Organic Vitamin D3',
                        'description': 'High-potency vitamin D3 supplement from organic sources',
                        'composition': 'Organic vitamin D3 (cholecalciferol), organic olive oil',
                        'usage_instructions': 'Take 1 capsule daily with food',
                        'creation_method': 'Extracted from organic lichen sources',
                        'benefits': 'Supports bone health, immune function, and overall wellness'
                    },
                    'fr': {
                        'name': 'Vitamine D3 Biologique',
                        'description': 'Supplément de vitamine D3 haute puissance de sources biologiques',
                        'composition': 'Vitamine D3 biologique (cholécalciférol), huile d\'olive biologique',
                        'usage_instructions': 'Prendre 1 capsule par jour avec de la nourriture',
                        'creation_method': 'Extrait de sources de lichen biologiques',
                        'benefits': 'Soutient la santé osseuse, la fonction immunitaire et le bien-être général'
                    },
                    'de': {
                        'name': 'Bio-Vitamin D3',
                        'description': 'Hochpotentes Vitamin D3-Supplement aus biologischen Quellen',
                        'composition': 'Bio-Vitamin D3 (Cholecalciferol), Bio-Olivenöl',
                        'usage_instructions': '1 Kapsel täglich mit dem Essen einnehmen',
                        'creation_method': 'Aus biologischen Flechtenquellen extrahiert',
                        'benefits': 'Unterstützt Knochengesundheit, Immunfunktion und allgemeines Wohlbefinden'
                    },
                    'es': {
                        'name': 'Vitamina D3 Orgánica',
                        'description': 'Suplemento de vitamina D3 de alta potencia de fuentes orgánicas',
                        'composition': 'Vitamina D3 orgánica (colecalciferol), aceite de oliva orgánico',
                        'usage_instructions': 'Tomar 1 cápsula diaria con comida',
                        'creation_method': 'Extraído de fuentes de líquenes orgánicos',
                        'benefits': 'Apoya la salud ósea, función inmune y bienestar general'
                    },
                    'it': {
                        'name': 'Vitamina D3 Biologica',
                        'description': 'Integratore di vitamina D3 ad alta potenza da fonti biologiche',
                        'composition': 'Vitamina D3 biologica (colecalciferolo), olio d\'oliva biologico',
                        'usage_instructions': 'Assumere 1 capsula al giorno con il cibo',
                        'creation_method': 'Estratto da fonti di licheni biologici',
                        'benefits': 'Supporta la salute delle ossa, la funzione immunitaria e il benessere generale'
                    }
                }
            }
        ]
        
        for prod_data in products_data:
            product, created = Product.objects.get_or_create(
                slug=prod_data['slug'],
                defaults={
                    'category': prod_data['category'],
                    'price': prod_data['price'],
                    'stock_quantity': 100,
                    'is_active': True,
                    'featured': True
                }
            )
            
            for lang_code, translation in prod_data['translations'].items():
                activate(lang_code)
                product.name = translation['name']
                product.description = translation['description']
                product.composition = translation['composition']
                product.usage_instructions = translation['usage_instructions']
                product.creation_method = translation['creation_method']
                product.benefits = translation['benefits']
                product.save()
            
            activate('en')  # Reset to English
        
        self.stdout.write(f'Created {len(products_data)} products with translations')