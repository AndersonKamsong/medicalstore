from django.core.management.base import BaseCommand

from pages.models import SiteSettings
from products.models import Category, Product

# ---------------------------------------------------------------------------
# All 20 categories from the original SQLite database
# ---------------------------------------------------------------------------
CATEGORIES = [
    {
        'slug': 'thc-flower',
        'name': 'THC Flower',
        'name_en': 'THC Flower',
        'name_fr': 'Fleurs THC',
        'description_en': 'High-quality cannabis flowers with significant THC content',
        'description_fr': 'Fleurs de cannabis de haute qualité avec une teneur significative en THC',
        'meta_description_en': 'Premium THC cannabis flowers for various needs',
        'meta_keywords_en': 'THC flower, cannabis, marijuana, buds',
        'strain_type': 'Hybrid',
        'preferred_ratio': 'high_thc',
        'recommended_methods': ['flower', 'vapes'],
        'primary_benefits': 'Pain relief, relaxation, appetite stimulation',
        'dosage_advice': 'Start with small amounts (0.1g) and wait 2 hours before additional doses',
        'effects_timeline': 'Effects begin within 5-15 minutes when smoked, lasting 2-4 hours',
        'storage_advice': 'Store in airtight glass containers away from light and heat',
        'icon': 'fas fa-cannabis',
        'is_medical': True,
        'is_recreational': True,
    },
    {
        'slug': 'cbd-flower',
        'name': 'CBD Flower',
        'name_en': 'CBD Flower',
        'name_fr': 'Fleurs CBD',
        'description_en': 'Premium CBD-rich cannabis flowers with minimal THC content',
        'description_fr': 'Fleurs de cannabis riches en CBD premium avec une teneur minimale en THC',
        'meta_description_en': 'Therapeutic CBD flowers for wellness without intoxication',
        'meta_keywords_en': 'CBD flower, hemp, therapeutic, non-psychoactive',
        'strain_type': 'Sativa',
        'preferred_ratio': 'high_cbd',
        'recommended_methods': ['flower', 'oil'],
        'primary_benefits': 'Anxiety relief, anti-inflammatory, neuroprotective',
        'dosage_advice': 'Dose as needed, typically 0.5-1g per session',
        'effects_timeline': 'Effects begin within 15-30 minutes, lasting 4-6 hours',
        'storage_advice': 'Store in cool, dark place with humidity control',
        'icon': 'fas fa-leaf',
        'is_medical': True,
        'is_recreational': False,
    },
    {
        'slug': 'backpack-boyz',
        'name': 'Backpack Boyz',
        'name_en': 'Backpack Boyz',
        'name_fr': 'Backpack Boyz',
        'description_en': 'Premium cannabis brand known for exotic strains and quality craftsmanship',
        'description_fr': (
            'Marque de cannabis premium reconnue pour ses variétés exotiques, son artisanat raffiné '
            'et ses techniques de culture innovantes. Appréciée tant par les patients médicaux que '
            'les utilisateurs récréatifs recherchant bien-être et expérience sensorielle.'
        ),
        'meta_description_en': 'Explore Backpack Boyz premium cannabis strains and products',
        'meta_keywords_en': 'Backpack Boyz, premium cannabis, exotic strains',
        'strain_type': 'Hybrid',
        'preferred_ratio': 'high_thc',
        'recommended_methods': ['flower', 'pre-rolls'],
        'primary_benefits': 'Creative stimulation, euphoria, relaxation',
        'dosage_advice': 'Start with 0.25g due to high potency',
        'effects_timeline': 'Effects begin within 10 minutes, lasting 2-3 hours',
        'storage_advice': 'Store in original packaging with humidity control',
        'icon': 'fas fa-backpack',
        'is_medical': True,
        'is_recreational': True,
    },
    {
        'slug': 'doja-exclusive',
        'name': 'Doja Exclusive',
        'name_en': 'Doja Exclusive',
        'name_fr': 'Doja Exclusive',
        'description_en': 'Luxury cannabis brand offering exclusive, small-batch cultivars',
        'description_fr': (
            'Marque de cannabis de luxe proposant des cultivars exclusifs en petites quantités, '
            'cultivés avec précision et soin. Destinée aux connaisseurs à la recherche d\'une '
            'qualité supérieure, de génétiques uniques et d\'une expérience raffinée.'
        ),
        'meta_description_en': "Discover Doja Exclusive's limited edition cannabis strains",
        'meta_keywords_en': 'Doja, exclusive cannabis, luxury strains',
        'strain_type': 'Indica',
        'preferred_ratio': 'balanced',
        'recommended_methods': ['flower', 'concentrates'],
        'primary_benefits': 'Stress relief, deep relaxation, sleep aid',
        'dosage_advice': '0.3g recommended for evening use',
        'effects_timeline': 'Effects begin within 20 minutes, lasting 3-4 hours',
        'storage_advice': 'Store in cool environment with Boveda pack',
        'icon': 'fas fa-crown',
        'is_medical': True,
        'is_recreational': True,
    },
    {
        'slug': 'jungle-boys',
        'name': 'Jungle Boys',
        'name_en': 'Jungle Boys',
        'name_fr': 'Jungle Boys',
        'description_en': 'Award-winning cultivators specializing in top-shelf cannabis genetics',
        'description_fr': (
            'Des cultivateurs primés de cannabis de luxe, spécialisés dans des génétiques rares '
            'produites en petites quantités, pour les connaisseurs en quête de pureté, puissance '
            'et arômes d\'exception.'
        ),
        'meta_description_en': 'Jungle Boys premium cannabis strains and genetics',
        'meta_keywords_en': 'Jungle Boys, cannabis genetics, award-winning',
        'strain_type': 'Hybrid',
        'preferred_ratio': 'high_thc',
        'recommended_methods': ['flower', 'vapes'],
        'primary_benefits': 'Mood elevation, pain relief, appetite stimulation',
        'dosage_advice': '0.2g recommended for first-time users',
        'effects_timeline': 'Effects begin within 5-15 minutes, lasting 2-3 hours',
        'storage_advice': 'Store in glass jars with humidity control',
        'icon': 'fas fa-leaf',
        'is_medical': True,
        'is_recreational': True,
    },
    {
        'slug': 'the-ten-co',
        'name': 'The TEN Co',
        'name_en': 'The TEN Co',
        'name_fr': 'The TEN Co',
        'description_en': 'Craft cannabis brand focusing on the top 10% of quality strains',
        'description_fr': (
            'Marque de cannabis artisanale se concentrant sur les 10% meilleures variétés de qualité. '
            'Chaque lot est sélectionné à la main et cultivé dans un environnement strictement contrôlé '
            'pour garantir une saveur, une puissance et une pureté haut de gamme aux connaisseurs '
            'en quête d\'excellence.'
        ),
        'meta_description_en': "The TEN Co's curated selection of premium cannabis",
        'meta_keywords_en': 'The TEN Co, craft cannabis, top 10% strains',
        'strain_type': 'Sativa',
        'preferred_ratio': 'high_thc',
        'recommended_methods': ['flower', 'pre-rolls'],
        'primary_benefits': 'Energy boost, focus enhancement, creativity',
        'dosage_advice': '0.15g recommended for daytime use',
        'effects_timeline': 'Effects begin within 10 minutes, lasting 1.5-2 hours',
        'storage_advice': 'Store in vacuum-sealed containers',
        'icon': 'fas fa-star',
        'is_medical': False,
        'is_recreational': True,
    },
    {
        'slug': 'wizard-trees',
        'name': 'Wizard Trees',
        'name_en': 'Wizard Trees',
        'name_fr': 'Wizard Trees',
        'description_en': 'Magical cannabis strains with unique terpene profiles and effects',
        'description_fr': (
            'Variétés de cannabis magiques avec des profils de terpènes et des effets uniques, '
            'offrant un mélange mystique d\'arômes et de bienfaits thérapeutiques. Chaque variété '
            'procure une expérience distincte, soigneusement cultivée pour améliorer l\'humeur, '
            'la créativité et la détente tout en délivrant des propriétés médicinales puissantes.'
        ),
        'meta_description_en': 'Wizard Trees mystical cannabis strains and products',
        'meta_keywords_en': 'Wizard Trees, magical cannabis, unique terpenes',
        'strain_type': 'Hybrid',
        'preferred_ratio': 'balanced',
        'recommended_methods': ['flower', 'concentrates'],
        'primary_benefits': 'Euphoria, relaxation, sensory enhancement',
        'dosage_advice': '0.2g recommended for optimal experience',
        'effects_timeline': 'Effects begin within 15 minutes, lasting 2.5-3 hours',
        'storage_advice': 'Store in dark glass containers with humidity control',
        'icon': 'fas fa-hat-wizard',
        'is_medical': True,
        'is_recreational': True,
    },
    {
        'slug': 'cookies-strains',
        'name': 'Cookies Strains',
        'name_en': 'Cookies Strains',
        'name_fr': 'Cookies Strains',
        'description_en': 'Iconic cannabis brand known for its legendary strains and quality',
        'description_fr': (
            'Marque de cannabis emblématique connue pour ses variétés légendaires et sa qualité '
            'exceptionnelle, profondément enracinée dans la culture et l\'histoire du cannabis. '
            'Réputée pour ses génétiques pionnières et son artisanat constant, cette marque '
            'représente l\'excellence dans la culture de produits supérieurs qui inspirent aussi '
            'bien les connaisseurs que les novices.'
        ),
        'meta_description_en': 'Cookies premium cannabis strains and products',
        'meta_keywords_en': 'Cookies, cannabis strains, premium genetics',
        'strain_type': 'Hybrid',
        'preferred_ratio': 'high_thc',
        'recommended_methods': ['flower', 'edibles'],
        'primary_benefits': 'Euphoria, relaxation, stress relief',
        'dosage_advice': '0.25g recommended for standard dose',
        'effects_timeline': 'Effects begin within 10-20 minutes, lasting 2-3 hours',
        'storage_advice': 'Store in original Cookies packaging',
        'icon': 'fas fa-cookie',
        'is_medical': True,
        'is_recreational': True,
    },
    {
        'slug': 'hash',
        'name': 'Hash',
        'name_en': 'Hash',
        'name_fr': 'Hash',
        'description_en': 'Traditional cannabis concentrate made from compressed resin glands',
        'description_fr': (
            'Concentré de cannabis traditionnel fabriqué à partir de glandes résineuses compressées, '
            'prisé pour sa pureté et sa puissance. Extrait avec soin selon des méthodes ancestrales '
            'afin de préserver les profils naturels de terpènes et le contenu en cannabinoïdes, '
            'offrant une expérience puissante et savoureuse pour les connaisseurs.'
        ),
        'meta_description_en': 'Premium quality hashish products from top producers',
        'meta_keywords_en': 'hash, hashish, cannabis concentrate, traditional',
        'strain_type': 'Hybrid',
        'preferred_ratio': 'high_thc',
        'recommended_methods': ['flower', 'edibles'],
        'primary_benefits': 'Pain relief, relaxation, euphoria',
        'dosage_advice': 'Start with 0.1g and wait 45 minutes before additional doses',
        'effects_timeline': 'Effects begin within 15-30 minutes, lasting 3-5 hours',
        'storage_advice': 'Store in parchment paper inside airtight container',
        'icon': 'fas fa-cube',
        'is_medical': True,
        'is_recreational': True,
    },
    {
        'slug': 'thc-diamond',
        'name': 'THC Diamonds',
        'name_en': 'THC Diamonds',
        'name_fr': 'Diamant de THC',
        'description_en': 'Ultra-pure THC crystals with exceptional potency and clarity',
        'description_fr': (
            'Cristaux de THC ultra-purs avec une puissance et une clarté exceptionnelles, '
            'minutieusement élaborés grâce à des techniques d\'extraction avancées. Réputés pour '
            'offrir un effet puissant et pur avec un minimum d\'impuretés, ces cristaux garantissent '
            'une constance inégalée et une expérience douce appréciée des connaisseurs et des '
            'utilisateurs médicaux.'
        ),
        'meta_description_en': 'Premium THC diamonds for connoisseurs and medical users',
        'meta_keywords_en': 'THC diamonds, cannabis extract, high potency',
        'strain_type': 'Other',
        'preferred_ratio': 'high_thc',
        'recommended_methods': ['dabbing', 'vapes'],
        'primary_benefits': 'Strong euphoria, pain relief, appetite stimulation',
        'dosage_advice': 'Extremely potent - start with 0.01g doses',
        'effects_timeline': 'Effects begin almost immediately, lasting 2-3 hours',
        'storage_advice': 'Store in silicone container away from light and heat',
        'icon': 'fas fa-gem',
        'is_medical': True,
        'is_recreational': True,
    },
    {
        'slug': 'thc-candy',
        'name': 'THC Candy',
        'name_en': 'THC Candy',
        'name_fr': 'Bonbons THC',
        'description_en': 'Delicious THC-infused candies for precise dosing and enjoyment',
        'description_fr': (
            'Délicieux bonbons infusés au THC élaborés avec des ingrédients naturels pour un dosage '
            'précis et des effets agréables. Parfaitement équilibrés pour les débutants comme pour '
            'les utilisateurs expérimentés, ces friandises offrent une puissance constante, une saveur '
            'douce et une relaxation durable, rendant chaque dose délicieuse.'
        ),
        'meta_description_en': 'Tasty THC candies in various flavors and potencies',
        'meta_keywords_en': 'THC candy, cannabis edibles, gummies',
        'strain_type': 'Other',
        'preferred_ratio': 'balanced',
        'recommended_methods': ['edibles'],
        'primary_benefits': 'Long-lasting effects, discreet consumption, flavor variety',
        'dosage_advice': 'Start with 5mg and wait 2 hours before additional doses',
        'effects_timeline': 'Effects begin within 30-90 minutes, lasting 4-8 hours',
        'storage_advice': 'Store in cool, dry place away from children',
        'icon': 'fas fa-candy-cane',
        'is_medical': False,
        'is_recreational': True,
    },
    {
        'slug': 'thc-oil',
        'name': 'THC Oil',
        'name_en': 'THC Oil',
        'name_fr': 'Huile THC',
        'description_en': 'Versatile THC oil for sublingual use, cooking, or vaporization',
        'description_fr': (
            'Huile THC polyvalente conçue pour une utilisation sublinguale, la cuisine ou la '
            'vaporisation. Élaborée pour la pureté et la puissance, cette huile offre un dosage '
            'précis et une saveur douce, ce qui la rend idéale pour diverses méthodes de '
            'consommation. Qu\'elle soit utilisée sous la langue pour une absorption rapide, '
            'infusée dans des recettes pour la créativité culinaire ou vaporisée pour des effets '
            'immédiats, elle offre une expérience constante et agréable.'
        ),
        'meta_description_en': 'High-quality THC oil in various concentrations',
        'meta_keywords_en': 'THC oil, cannabis oil, tincture',
        'strain_type': 'Other',
        'preferred_ratio': 'high_thc',
        'recommended_methods': ['oil', 'edibles'],
        'primary_benefits': 'Fast absorption, customizable dosing, versatile use',
        'dosage_advice': 'Start with 0.25ml (typically 5mg THC) and wait 1 hour',
        'effects_timeline': 'Sublingual: 15-30 mins onset, 3-5 hours duration',
        'storage_advice': 'Store in dark glass bottle in cool place',
        'icon': 'fas fa-oil-can',
        'is_medical': True,
        'is_recreational': True,
    },
    {
        'slug': 'cbd-oil',
        'name': 'CBD Oil',
        'name_en': 'CBD Oil',
        'name_fr': 'Huile CBD',
        'description_en': 'Premium CBD oil extracted from organic hemp, available in various concentrations',
        'description_fr': (
            'Huile de CBD de qualité supérieure, extraite avec soin de chanvre biologique. '
            'Parfaite pour les routines bien-être quotidiennes, la gestion du stress et '
            'l\'amélioration du sommeil. Disponible en plusieurs concentrations adaptées à vos besoins.'
        ),
        'meta_description_en': 'High-quality CBD oil for wellness and therapeutic use',
        'meta_keywords_en': 'CBD oil, hemp extract, wellness, therapeutic',
        'strain_type': 'Other',
        'preferred_ratio': 'high_cbd',
        'recommended_methods': ['oil', 'sublingual'],
        'primary_benefits': 'Anxiety relief, pain management, anti-inflammatory',
        'dosage_advice': 'Start with 10mg CBD, adjust as needed',
        'effects_timeline': 'Effects begin within 15-45 minutes, lasting 4-6 hours',
        'storage_advice': 'Store in cool, dark place away from sunlight',
        'icon': 'fas fa-tint',
        'is_medical': True,
        'is_recreational': False,
    },
    {
        'slug': 'cannabis-tincture',
        'name': 'Cannabis Tincture',
        'name_en': 'Cannabis Tincture',
        'name_fr': 'Teinture Cannabis',
        'description_en': 'Alcohol-based cannabis extract for precise sublingual dosing',
        'description_fr': (
            'Extrait de cannabis à base d\'alcool conçu pour un dosage sublingual précis, '
            'garantissant une absorption rapide et un soulagement efficace des symptômes. '
            'Idéal pour une consommation discrète et maîtrisée.'
        ),
        'meta_description_en': 'Traditional cannabis tinctures for accurate medicinal use',
        'meta_keywords_en': 'cannabis tincture, alcohol extract, sublingual',
        'strain_type': 'Other',
        'preferred_ratio': 'balanced',
        'recommended_methods': ['oil', 'sublingual'],
        'primary_benefits': 'Fast absorption, customizable dosing, long shelf life',
        'dosage_advice': 'Start with 0.5ml under tongue, hold for 60 seconds',
        'effects_timeline': 'Effects begin within 15-30 minutes, lasting 4-6 hours',
        'storage_advice': 'Store in dark glass bottle at room temperature',
        'icon': 'fas fa-flask',
        'is_medical': True,
        'is_recreational': False,
    },
    {
        'slug': 'magic-mushrooms',
        'name': 'Magic Mushrooms',
        'name_en': 'Magic Mushrooms',
        'name_fr': 'Champignons magiques',
        'description_en': 'Psychedelic mushrooms containing psilocybin for therapeutic and spiritual use',
        'description_fr': (
            'Champignons psychédéliques contenant de la psilocybine, un composé psychoactif naturel '
            'provoquant des états modifiés de conscience. Utilisés traditionnellement par les cultures '
            'autochtones lors de rituels spirituels et de guérison, ils sont aujourd\'hui étudiés '
            'pour leurs bienfaits thérapeutiques contre la dépression, l\'anxiété, le PTSD et les addictions.'
        ),
        'meta_description_en': 'Premium quality psilocybin mushrooms for mindful exploration',
        'meta_keywords_en': 'magic mushrooms, psilocybin, psychedelic, therapeutic',
        'strain_type': 'Other',
        'preferred_ratio': None,
        'recommended_methods': ['edibles', 'tea'],
        'primary_benefits': 'Mental health support, spiritual growth, creativity',
        'dosage_advice': 'Start with 1g dried mushrooms, wait 2 hours before redosing',
        'effects_timeline': 'Effects begin within 20-40 minutes, lasting 4-6 hours',
        'storage_advice': 'Store in airtight container with desiccant in freezer',
        'icon': 'fas fa-mushroom',
        'is_medical': False,
        'is_recreational': True,
    },
    {
        'slug': 'pain-relief',
        'name': 'Pain Relief',
        'name_en': 'Pain Relief',
        'name_fr': None,
        'description_en': (
            'Effective pain management solutions for various conditions including chronic pain, '
            'acute injuries, and post-operative care.'
        ),
        'description_fr': None,
        'meta_description_en': 'Professional pain relief products with detailed composition and usage instructions.',
        'meta_keywords_en': 'pain relief, analgesics, pain management, medical products',
        'strain_type': None,
        'preferred_ratio': None,
        'recommended_methods': None,
        'primary_benefits': '',
        'dosage_advice': '',
        'effects_timeline': '',
        'storage_advice': '',
        'icon': 'fas fa-pills',
        'is_medical': True,
        'is_recreational': False,
    },
    {
        'slug': 'cardiovascular-health',
        'name': 'Cardiovascular Health',
        'name_en': 'Cardiovascular Health',
        'name_fr': None,
        'description_en': (
            'Comprehensive cardiovascular support products designed to promote heart health '
            'and circulatory system function.'
        ),
        'description_fr': None,
        'meta_description_en': 'Cardiovascular health products with proven benefits and scientific backing.',
        'meta_keywords_en': 'cardiovascular, heart health, circulation, blood pressure',
        'strain_type': None,
        'preferred_ratio': None,
        'recommended_methods': None,
        'primary_benefits': '',
        'dosage_advice': '',
        'effects_timeline': '',
        'storage_advice': '',
        'icon': 'fas fa-heartbeat',
        'is_medical': True,
        'is_recreational': False,
    },
    {
        'slug': 'digestive-health',
        'name': 'Digestive Health',
        'name_en': 'Digestive Health',
        'name_fr': None,
        'description_en': (
            'Digestive system support products for optimal gastrointestinal health '
            'and nutrient absorption.'
        ),
        'description_fr': None,
        'meta_description_en': 'Digestive health solutions with detailed composition and usage guidelines.',
        'meta_keywords_en': 'digestive health, gastrointestinal, probiotics, digestion',
        'strain_type': None,
        'preferred_ratio': None,
        'recommended_methods': None,
        'primary_benefits': '',
        'dosage_advice': '',
        'effects_timeline': '',
        'storage_advice': '',
        'icon': 'fas fa-stomach',
        'is_medical': True,
        'is_recreational': False,
    },
    {
        'slug': 'immune-support',
        'name': 'Immune Support',
        'name_en': 'Immune Support',
        'name_fr': None,
        'description_en': (
            'Immune system strengthening products to help maintain optimal immune function '
            'and overall wellness.'
        ),
        'description_fr': None,
        'meta_description_en': 'Immune support products with comprehensive health benefits information.',
        'meta_keywords_en': 'immune support, immunity, wellness, health supplements',
        'strain_type': None,
        'preferred_ratio': None,
        'recommended_methods': None,
        'primary_benefits': '',
        'dosage_advice': '',
        'effects_timeline': '',
        'storage_advice': '',
        'icon': 'fas fa-shield-alt',
        'is_medical': True,
        'is_recreational': False,
    },
    {
        'slug': 'respiratory-care',
        'name': 'Respiratory Care',
        'name_en': 'Respiratory Care',
        'name_fr': None,
        'description_en': (
            'Respiratory health products designed to support lung function and breathing comfort.'
        ),
        'description_fr': None,
        'meta_description_en': 'Respiratory care products with detailed usage instructions and benefits.',
        'meta_keywords_en': 'respiratory care, lung health, breathing, pulmonary',
        'strain_type': None,
        'preferred_ratio': None,
        'recommended_methods': None,
        'primary_benefits': '',
        'dosage_advice': '',
        'effects_timeline': '',
        'storage_advice': '',
        'icon': 'fas fa-lungs',
        'is_medical': True,
        'is_recreational': False,
    },
]

# ---------------------------------------------------------------------------
# All 17 products from the original SQLite database
# image is intentionally omitted — upload via admin to Cloudinary
# ---------------------------------------------------------------------------
PRODUCTS = [
    # ── Cannabis products (category: thc-flower) ────────────────────────────
    {
        'slug': 'ak-47',
        'category_slug': 'thc-flower',
        'name': 'AK-47',
        'name_en': 'AK-47',
        'name_fr': 'AK-47',
        'price': '210.00',
        'stock_quantity': 50,
        'is_active': True,
        'featured': True,
        'strain_type': None,
        'preferred_ratio': None,
        'recommended_methods': ['vaporizing', 'smoking', 'concentrates'],
        'average_rating': '4.75',
        'rating_count': 4,
        'description_en': (
            'AK-47 is a legendary sativa-dominant hybrid (65% sativa/35% indica) known for its '
            'powerful cerebral effects and earthy, skunky aroma with subtle citrus undertones. '
            'This multiple Cannabis Cup winner features dense, resinous buds with fiery orange '
            'pistils. Delivers an energetic, creative high perfect for daytime use while maintaining '
            'functional clarity. Grown from original Serious Seeds genetics since 1992.'
        ),
        'description_fr': (
            "L'AK-47 est un hybride légendaire à dominance sativa (65% sativa/35% indica) réputé "
            'pour ses effets cérébraux puissants et son arôme terreux et skunk avec des nuances '
            "subtiles d'agrumes. Ce multiple vainqueur de la Cannabis Cup présente des buds denses "
            'et résineux avec des pistils orange vif. Produit un high énergique et créatif, parfait '
            'pour une utilisation diurne tout en maintenant une clarté fonctionnelle. Cultivé à '
            "partir de la génétique originale de Serious Seeds depuis 1992."
        ),
        'composition_en': (
            'THC: 18-24%, CBD: <1%, CBG: 0.3-0.8%. Dominant Terpenes: Myrcene (0.7%), Pinene (0.5%), '
            'Caryophyllene (0.4%), Limonene (0.3%), Terpinolene (0.2%). Minor Terpenes: Linalool, '
            'Humulene, Ocimene. Contains over 50 active cannabinoids and 120 terpenes in total.'
        ),
        'composition_fr': (
            'THC: 18-24%, CBD: <1%, CBG: 0,3-0,8%. Terpènes dominants: Myrcène (0,7%), Pinène (0,5%), '
            'Caryophyllène (0,4%), Limonène (0,3%), Terpinolène (0,2%). Terpènes mineurs: Linalol, '
            'Humulène, Ocimène. Contient plus de 50 cannabinoïdes actifs et 120 terpènes au total.'
        ),
        'usage_instructions_en': (
            'Recommended dosage: 0.1-0.25g for beginners, 0.25-0.5g for experienced users. Optimal '
            'consumption via vaporizer at 175-190°C to preserve delicate terpenes. For smoking, use '
            'clean glassware or hemp papers. Effects onset within 5-10 minutes, peaking at 30-60 '
            'minutes, lasting 2-3 hours. Maintain hydration and avoid combining with alcohol. Store '
            'in UV-protected airtight containers with 58-62% humidity packs at 18-22°C. Not '
            'recommended within 4 hours of bedtime.'
        ),
        'usage_instructions_fr': (
            'Dosage recommandé : 0,1-0,25g pour les débutants, 0,25-0,5g pour les utilisateurs '
            'expérimentés. Consommation optimale via vaporisateur à 175-190°C pour préserver les '
            'terpènes délicats. Pour fumer, utilisez du verre propre ou des papiers à rouler en '
            'chanvre. Effets en 5-10 minutes, pic à 30-60 minutes, durée 2-3 heures. Maintenez une '
            'bonne hydratation et évitez de combiner avec de l\'alcool. Conserver dans des contenants '
            'hermétiques protégés des UV avec des sachets humidificateurs à 58-62% à 18-22°C. Non '
            'recommandé dans les 4 heures précédant le coucher.'
        ),
        'creation_method_en': (
            'Cultivated using advanced hydroponic systems under full-spectrum LED lighting with 20/4 '
            'vegetative cycle and 12/12 flowering cycle. Hand-trimmed using chilled scissors to '
            'preserve trichome integrity, then slow-dried for 10-14 days at 17°C and 50% humidity. '
            'Cured in dark glass jars with Boveda 62% packs for minimum 45 days, with bi-weekly '
            'burping. Each batch undergoes third-party lab testing for cannabinoids (18+ panels), '
            'terpenes (30+ profiles), and contaminants (pesticides, heavy metals, microbes).'
        ),
        'creation_method_fr': (
            'Cultivé en utilisant des systèmes hydroponiques avancés sous éclairage LED à spectre '
            'complet avec un cycle végétatif 20/4 et un cycle de floraison 12/12. Taillé à la main '
            'avec des ciseaux refroidis pour préserver l\'intégrité des trichomes, puis séché '
            'lentement pendant 10-14 jours à 17°C et 50% d\'humidité. Affiné dans des bocaux en '
            'verre foncé avec des sachets Boveda 62% pendant au moins 45 jours, avec dégazage '
            'bi-hebdomadaire. Chaque lot est testé par un laboratoire tiers pour les cannabinoïdes '
            '(18+ panels), les terpènes (30+ profils) et les contaminants (pesticides, métaux lourds, microbes).'
        ),
        'benefits_en': (
            'Primary therapeutic applications: Mood elevation for depression/anxiety, chronic pain '
            'management (especially migraines and neuropathic pain), fatigue relief, appetite '
            'stimulation without sedation, creative flow enhancement. Secondary benefits: May help '
            'with ADHD focus at low doses, social anxiety reduction. Contraindications: Not '
            'recommended for individuals prone to paranoia or with heart conditions. May temporarily '
            'increase blood pressure. Always consult a healthcare provider before medical use. '
            'Synergistic when combined with CBD-rich strains for balanced effects.'
        ),
        'benefits_fr': (
            'Applications thérapeutiques primaires : Élévation de l\'humeur pour dépression/anxiété, '
            'gestion de la douleur chronique (surtout migraines et douleur neuropathique), soulagement '
            'de la fatigue, stimulation de l\'appétit sans sédation, amélioration du flux créatif. '
            'Avantages secondaires : Peut aider à la concentration du TDAH à faible dose, réduction '
            'de l\'anxiété sociale. Contre-indications : Non recommandé aux personnes sujettes à la '
            'paranoïa ou avec des problèmes cardiaques. Peut augmenter temporairement la tension '
            'artérielle. Consultez toujours un professionnel de la santé avant un usage médical. '
            'Synergique lorsqu\'il est combiné avec des variétés riches en CBD pour des effets équilibrés.'
        ),
        'meta_description_en': (
            'Premium AK-47 cannabis flowers - 65% sativa/35% indica hybrid with 18-24% THC. '
            'Multiple Cannabis Cup winner with energetic cerebral effects. Lab-tested for purity '
            'and terpene profile. Organically grown, hand-trimmed, and slow-cured for maximum '
            'potency. Ideal for daytime creative sessions and mood elevation.'
        ),
        'meta_keywords_en': (
            'ak47, cannabis, sativa, hybrid, thc, marijuana, weed, creative strain, energy boost, '
            'mood lifter, cannabis cup winner'
        ),
    },
    {
        'slug': 'alien-og',
        'category_slug': 'thc-flower',
        'name': 'Alien OG',
        'name_en': 'Alien OG',
        'name_fr': 'Alien OG',
        'price': '235.00',
        'stock_quantity': 35,
        'is_active': True,
        'featured': True,
        'strain_type': 'Indica',
        'preferred_ratio': None,
        'recommended_methods': ['smoking', 'vaporizing', 'edibles'],
        'average_rating': '0.00',
        'rating_count': 0,
        'description_en': (
            'Alien OG is a powerful indica-dominant hybrid (80% indica/20% sativa) originating '
            'from the legendary OG Kush and Alien Kush strains. Known for its heavy body relaxation '
            'and euphoric cerebral effects, it features dense olive-green buds with purple hues, '
            'coated in crystal trichomes. The complex aroma combines earthy pine with sharp citrus '
            'notes and a subtle diesel undertone. Ideal for evening use, it provides deep physical '
            'relief while maintaining mental clarity.'
        ),
        'description_fr': (
            "L'Alien OG est un hybride puissant à dominance indica (80% indica/20% sativa) issu des "
            'légendaires variétés OG Kush et Alien Kush. Réputé pour sa relaxation corporelle profonde '
            'et ses effets cérébraux euphorisants, il présente des buds denses vert olive avec des '
            'reflets violets, recouverts de trichomes cristallins. Son arôme complexe combine des '
            "notes terreuses de pin avec des accents d'agrumes vifs et une subtile touche diesel. "
            'Idéal pour une utilisation en soirée, il procure un soulagement physique profond tout '
            'en maintenant une clarté mentale.'
        ),
        'composition_en': (
            'THC: 20-26%, CBD: <1%, CBG: 0.5-1.5%. Dominant Terpenes: Limonene (0.8%), Myrcene (0.6%), '
            'Linalool (0.4%), Caryophyllene (0.3%), Pinene (0.2%). Minor Terpenes: Humulene, '
            'Terpinolene, Ocimene.'
        ),
        'composition_fr': (
            'THC: 20-26%, CBD: <1%, CBG: 0,5-1,5%. Terpènes dominants: Limonène (0,8%), Myrcène (0,6%), '
            'Linalol (0,4%), Caryophyllène (0,3%), Pinène (0,2%). Terpènes mineurs: Humulène, '
            'Terpinolène, Ocimène.'
        ),
        'usage_instructions_en': (
            'Recommended dosage: 0.1-0.3g for beginners, 0.3-0.5g for experienced users. Best consumed '
            'via dry herb vaporizer at 185-210°C for optimal terpene preservation. For smoking, use '
            'clean glassware. Effects begin within 5-15 minutes, peaking at 45-90 minutes, with total '
            'duration of 2-4 hours. Avoid operating heavy machinery for 6 hours after consumption. '
            'Store in an airtight container with 62% humidity control at 18-21°C away from direct light.'
        ),
        'usage_instructions_fr': (
            'Dosage recommandé : 0,1-0,3g pour les débutants, 0,3-0,5g pour les utilisateurs '
            'expérimentés. À consommer de préférence avec un vaporisateur à herbe sèche à 185-210°C '
            'pour une préservation optimale des terpènes. Pour fumer, utilisez du verre propre. Les '
            'effets commencent en 5-15 minutes, culminent à 45-90 minutes, avec une durée totale de '
            '2-4 heures. Évitez d\'utiliser des machines lourdes pendant 6 heures après consommation. '
            'Conserver dans un récipient hermétique avec un contrôle d\'humidité à 62% à 18-21°C à '
            "l'abri de la lumière directe."
        ),
        'creation_method_en': (
            'Cultivated using living soil organic techniques under full-spectrum LED lighting with a '
            '18/6 light cycle during vegetation and 12/12 during flowering. Hand-trimmed while fresh '
            'to preserve trichome integrity, then slow-dried for 14-21 days at 16°C and 55% humidity. '
            'Cured in glass jars with Boveda 62% packs for 60+ days, with weekly burping. Each batch '
            'is lab-tested for cannabinoid and terpene profiles, with microbial and heavy metal screening.'
        ),
        'creation_method_fr': (
            'Cultivé en utilisant des techniques biologiques de sol vivant sous un éclairage LED à '
            'spectre complet avec un cycle lumineux de 18/6 pendant la végétation et 12/12 pendant la '
            'floraison. Taillé à la main lorsqu\'il est frais pour préserver l\'intégrité des trichomes, '
            'puis séché lentement pendant 14-21 jours à 16°C et 55% d\'humidité. Affiné dans des bocaux '
            'en verre avec des sachets Boveda 62% pendant 60+ jours, avec dégazage hebdomadaire. Chaque '
            'lot est testé en laboratoire pour les profils de cannabinoïdes et de terpènes, avec '
            'dépistage microbien et des métaux lourds.'
        ),
        'benefits_en': (
            'Primary therapeutic applications: Chronic pain management (especially neuropathic and '
            'inflammatory pain), insomnia relief, muscle spasm reduction, appetite stimulation for '
            'chemotherapy patients, anxiety and PTSD symptom relief. Secondary benefits: Mild euphoria '
            'and creativity enhancement without sedation at lower doses, may help with depression '
            'symptoms. Contraindications: Not recommended for individuals with low THC tolerance or '
            'predisposition to cannabis-induced anxiety. Always consult a medical professional before '
            'use for therapeutic purposes.'
        ),
        'benefits_fr': (
            'Applications thérapeutiques primaires : Gestion de la douleur chronique (surtout '
            'neuropathique et inflammatoire), soulagement de l\'insomnie, réduction des spasmes '
            'musculaires, stimulation de l\'appétit pour les patients sous chimiothérapie, soulagement '
            'des symptômes d\'anxiété et de TSPT. Avantages secondaires : Euphorie légère et '
            'amélioration de la créativité sans sédation à faible dose, peut aider avec les symptômes '
            'de dépression. Contre-indications : Non recommandé pour les personnes ayant une faible '
            'tolérance au THC ou une prédisposition à l\'anxiété induite par le cannabis. Consultez '
            'toujours un professionnel de la santé avant d\'utiliser à des fins thérapeutiques.'
        ),
        'meta_description_en': (
            'Premium Alien OG cannabis flowers - 80% indica/20% sativa hybrid with 20-26% THC. '
            'Lab-tested for purity and potency. Ideal for evening use, providing deep relaxation and '
            'pain relief while maintaining mental clarity.'
        ),
        'meta_keywords_en': (
            'alien og, cannabis, indica, hybrid, thc, kush, marijuana, weed, medical cannabis, '
            'pain relief, insomnia, relaxation'
        ),
    },
    {
        'slug': 'amnesia-haze',
        'category_slug': 'thc-flower',
        'name': 'Amnesia Haze',
        'name_en': 'Amnesia Haze',
        'name_fr': 'Amnesia Haze',
        'price': '210.00',
        'stock_quantity': 40,
        'is_active': True,
        'featured': True,
        'strain_type': 'Sativa',
        'preferred_ratio': None,
        'recommended_methods': ['vaporizing', 'smoking', 'concentrates'],
        'average_rating': '0.00',
        'rating_count': 0,
        'description_en': (
            'Amnesia Haze is a legendary sativa-dominant hybrid (70% sativa/30% indica) with South '
            'Asian and Jamaican landrace genetics. Known for its intense cerebral effects and '
            'long-lasting euphoria, it features elongated lime-green buds with fiery orange pistils '
            'and a thick trichome coating. Multiple Cannabis Cup winner prized for its creative energy '
            'and social enhancement.'
        ),
        'description_fr': (
            "L'Amnesia Haze est un hybride légendaire à dominance sativa (70% sativa/30% indica) avec "
            "une génétique landrace d'Asie du Sud et de Jamaïque. Connu pour ses effets cérébraux "
            'intenses et son euphorie durable, il présente des buds allongés vert lime avec des pistils '
            'orange vif et un épais manteau de trichomes. Multiple vainqueur de la Cannabis Cup, prisé '
            'pour son énergie créative et ses propriétés sociales.'
        ),
        'composition_en': (
            'THC: 20-25%, CBD: <0.5%, CBG: 0.6-1.2%. Dominant Terpenes: Terpinolene (0.8%), Myrcene '
            '(0.6%), Pinene (0.5%), Ocimene (0.4%), Caryophyllene (0.3%). Minor Terpenes: Limonene, '
            'Linalool, Humulene. Contains over 120 identified cannabinoids and terpenes in synergistic ratios.'
        ),
        'composition_fr': (
            'THC: 20-25%, CBD: <0,5%, CBG: 0,6-1,2%. Terpènes dominants: Terpinolène (0,8%), Myrcène '
            '(0,6%), Pinène (0,5%), Ocimène (0,4%), Caryophyllène (0,3%). Terpènes mineurs: Limonène, '
            'Linalol, Humulène. Contient plus de 120 cannabinoïdes et terpènes identifiés dans des '
            'rapports synergiques.'
        ),
        'usage_instructions_en': (
            'Recommended dosage: 0.1-0.2g for beginners, 0.2-0.4g for experienced users. Optimal '
            'consumption via vaporizer at 165-180°C to preserve delicate terpenes. Effects onset within '
            '5-15 minutes, peaking at 45-90 minutes, lasting 3-5 hours. Best for daytime creative '
            'activities, social gatherings, or artistic pursuits. Avoid combining with alcohol or '
            'sedatives. Store in UV-protected glass jars with 58-62% humidity packs at 18-22°C.'
        ),
        'usage_instructions_fr': (
            'Dosage recommandé : 0,1-0,2g pour les débutants, 0,2-0,4g pour les utilisateurs '
            'expérimentés. Consommation optimale via vaporisateur à 165-180°C pour préserver les '
            'terpènes délicats. Effets en 5-15 minutes, pic à 45-90 minutes, durée 3-5 heures. Idéal '
            'pour les activités créatives diurnes, les rencontres sociales ou les activités artistiques. '
            'Éviter de combiner avec de l\'alcool ou des sédatifs. Conserver dans des bocaux en verre '
            'protégés des UV avec des sachets humidificateurs à 58-62% à 18-22°C.'
        ),
        'creation_method_en': (
            'Cultivated using organic living soil techniques under full-spectrum LED lighting. '
            'Hand-trimmed using cryo-cured techniques to preserve trichome integrity, then slow-dried '
            'for 14-21 days at 16°C and 55% humidity. Cured in dark glass jars with Boveda 62% packs '
            'for minimum 60 days, with weekly burping. Each batch undergoes third-party lab testing for '
            'cannabinoids (24+ panels), terpenes (40+ profiles), and contaminants.'
        ),
        'creation_method_fr': (
            'Cultivé en utilisant des techniques de sol vivant biologique sous éclairage LED à spectre '
            'complet. Taillé à la main en utilisant des techniques de cryo-affinage pour préserver '
            "l'intégrité des trichomes, puis séché lentement pendant 14-21 jours à 16°C et 55% "
            "d'humidité. Affiné dans des bocaux en verre foncé avec des sachets Boveda 62% pendant "
            'au moins 60 jours, avec dégazage hebdomadaire. Chaque lot est testé par un laboratoire '
            'tiers pour les cannabinoïdes (24+ panels), les terpènes (40+ profils) et les contaminants.'
        ),
        'benefits_en': (
            'Primary therapeutic applications: Treatment-resistant depression, chronic fatigue syndrome, '
            'ADHD focus enhancement, social anxiety relief, and PTSD symptom management. Secondary '
            'benefits: Creative flow state induction, sensory perception enhancement, mild analgesic '
            'effects. Contraindications: Not recommended for individuals with anxiety disorders or '
            'predisposition to psychosis. Always consult a healthcare professional before therapeutic use.'
        ),
        'benefits_fr': (
            'Applications thérapeutiques primaires : Dépression résistante au traitement, syndrome de '
            'fatigue chronique, amélioration de la concentration du TDAH, soulagement de l\'anxiété '
            'sociale et gestion des symptômes du TSPT. Avantages secondaires : Induction d\'un état de '
            'flux créatif, amélioration de la perception sensorielle, légers effets analgésiques. '
            'Contre-indications : Non recommandé aux personnes souffrant de troubles anxieux ou '
            'prédisposées à la psychose. Consultez toujours un professionnel de la santé avant une '
            'utilisation thérapeutique.'
        ),
        'meta_description_en': (
            'Premium Amnesia Haze cannabis flowers - 70% sativa/30% indica hybrid with 20-25% THC. '
            'Multiple Cannabis Cup winner with intense cerebral effects and long-lasting euphoria. '
            'Ideal for creative pursuits and social enhancement.'
        ),
        'meta_keywords_en': (
            'amnesia haze, cannabis, sativa, hybrid, thc, marijuana, weed, creative strain, euphoria, '
            'social enhancer, cannabis cup winner'
        ),
    },
    {
        'slug': 'apple-fritter',
        'category_slug': 'thc-flower',
        'name': 'Apple Fritter',
        'name_en': 'Apple Fritter',
        'name_fr': 'Apple Fritter',
        'price': '235.00',
        'stock_quantity': 35,
        'is_active': True,
        'featured': True,
        'strain_type': None,
        'preferred_ratio': None,
        'recommended_methods': ['vaporizing', 'smoking', 'edibles'],
        'average_rating': '4.51',
        'rating_count': 4,
        'description_en': (
            'Apple Fritter is a potent indica-dominant hybrid (60% indica/40% sativa) created by '
            'crossing Sour Apple and Animal Cookies. Famous for its delicious sweet apple and pastry '
            'aroma with hints of spicy earthiness, it produces dense, resinous buds with deep purple '
            'hues and vivid orange pistils. Delivers a balanced high that begins with cerebral euphoria '
            'before melting into full body relaxation. Multiple award winner prized for its exceptional '
            'flavor profile and versatile effects.'
        ),
        'description_fr': (
            "L'Apple Fritter est un hybride puissant à dominance indica (60% indica/40% sativa) issu "
            'du croisement entre Sour Apple et Animal Cookies. Célèbre pour son délicieux arôme sucré '
            'de pomme et de pâtisserie avec des notes de terre épicée, il produit des buds denses et '
            'résineux avec des teintes violet profond et des pistils orange vif. Offre un high équilibré '
            'qui commence par une euphorie cérébrale avant de se transformer en relaxation corporelle '
            'totale. Multiple vainqueur de prix, prisé pour son profil aromatique exceptionnel.'
        ),
        'composition_en': (
            'THC: 22-28%, CBD: <0.3%, CBG: 0.4-0.9%. Dominant Terpenes: Limonene (1.2%), Caryophyllene '
            '(0.8%), Linalool (0.6%), Myrcene (0.5%), Humulene (0.4%). Minor Terpenes: Pinene, '
            'Terpinolene, Ocimene. Contains unique ester compounds contributing to its pastry aroma profile.'
        ),
        'composition_fr': (
            'THC: 22-28%, CBD: <0,3%, CBG: 0,4-0,9%. Terpènes dominants: Limonène (1,2%), Caryophyllène '
            '(0,8%), Linalol (0,6%), Myrcène (0,5%), Humulène (0,4%). Terpènes mineurs: Pinène, '
            'Terpinolène, Ocimène. Contient des composés ester uniques contribuant à son profil '
            'aromatique de pâtisserie.'
        ),
        'usage_instructions_en': (
            'Recommended dosage: 0.15-0.3g for beginners, 0.3-0.6g for experienced users. Optimal '
            'consumption via vaporizer at 170-185°C to highlight its complex terpene profile. Effects '
            'begin within 10-20 minutes, peaking at 60-120 minutes, lasting 4-6 hours. Ideal for '
            'evening use when transitioning from activity to relaxation. Store in airtight containers '
            'with 62% humidity packs at 18-21°C away from direct light.'
        ),
        'usage_instructions_fr': (
            'Dosage recommandé : 0,15-0,3g pour les débutants, 0,3-0,6g pour les utilisateurs '
            'expérimentés. Consommation optimale via vaporisateur à 170-185°C pour mettre en valeur '
            'son profil terpénique complexe. Effets en 10-20 minutes, pic à 60-120 minutes, durée '
            '4-6 heures. Idéal pour une utilisation en soirée lors de la transition entre activité '
            'et relaxation.'
        ),
        'creation_method_en': (
            'Cultivated using organic super-soil techniques under dual-spectrum HPS/LED lighting. '
            'Hand-trimmed using nitrogen-cooled tools to prevent trichome damage, then slow-dried '
            'for 12-16 days at 17°C and 52% humidity. Cured in food-grade stainless steel containers '
            'with Boveda 62% packs for minimum 45 days, with bi-weekly burping.'
        ),
        'creation_method_fr': (
            'Cultivé en utilisant des techniques de super-sol organique sous éclairage HPS/LED double '
            'spectre. Taillé à la main avec des outils refroidis à l\'azote pour éviter d\'endommager '
            'les trichomes, puis séché lentement pendant 12-16 jours à 17°C et 52% d\'humidité. '
            'Affiné dans des conteneurs en acier inoxydable de qualité alimentaire avec des sachets '
            'Boveda 62% pendant au moins 45 jours, avec dégazage bi-hebdomadaire.'
        ),
        'benefits_en': (
            'Primary therapeutic applications: Chronic pain management (especially arthritis and '
            'fibromyalgia), appetite stimulation for cachexia patients, insomnia relief, PTSD symptom '
            'reduction and stress-related digestive issues. Secondary benefits: Mood enhancement without '
            'sedation, mild anti-inflammatory effects, may help with mild depression. Contraindications: '
            'Not recommended for individuals with low THC tolerance or diabetes due to potential '
            'appetite stimulation. Always consult a doctor before medical use.'
        ),
        'benefits_fr': (
            'Applications thérapeutiques primaires : Gestion de la douleur chronique (surtout arthrite '
            'et fibromyalgie), stimulation de l\'appétit pour les patients cachexiques, soulagement de '
            'l\'insomnie, réduction des symptômes du TSPT et problèmes digestifs liés au stress. '
            'Avantages secondaires : Élévation de l\'humeur sans sédation, légers effets anti-'
            'inflammatoires, peut aider en cas de dépression légère. Consultez toujours un professionnel '
            'de la santé avant une utilisation thérapeutique.'
        ),
        'meta_description_en': (
            'Premium Apple Fritter cannabis flowers - 60% indica/40% sativa hybrid with 22-28% THC. '
            'Multiple award winner with sweet apple-pastry aroma and balanced effects. Ideal for '
            'evening relaxation with mild cerebral stimulation.'
        ),
        'meta_keywords_en': (
            'apple fritter, cannabis, indica, hybrid, thc, dessert strain, sweet aroma, pain relief, relaxation'
        ),
    },
    {
        'slug': 'apple-jack',
        'category_slug': 'thc-flower',
        'name': 'Apple Jack',
        'name_en': 'Apple Jack',
        'name_fr': 'Apple Jack',
        'price': '235.00',
        'stock_quantity': 100,
        'is_active': True,
        'featured': True,
        'strain_type': None,
        'preferred_ratio': None,
        'recommended_methods': ['flower', 'vape'],
        'average_rating': '4.50',
        'rating_count': 5,
        'description_en': 'A perfectly balanced hybrid with sweet apple flavors and relaxing effects.',
        'description_fr': 'Un hybride parfaitement équilibré avec des saveurs de pomme douce et des effets relaxants.',
        'composition_en': 'THC: 18-22%, CBD: <1%, Terpenes: Myrcene, Pinene, Caryophyllene',
        'composition_fr': 'THC : 18-22 %, CBD : <1 %, Terpènes : Myrcène, Pinène, Caryophyllène',
        'usage_instructions_en': 'Start with small doses. Smoke or vaporize. Effects appear within minutes.',
        'usage_instructions_fr': 'Commencez par de petites doses. Fumez ou vaporisez. Les effets apparaissent en quelques minutes.',
        'creation_method_en': 'Indoor grown using organic methods, hand-trimmed, slow-cured for optimal flavor.',
        'creation_method_fr': 'Cultivé en intérieur selon des méthodes biologiques, taillé à la main, séché lentement pour une saveur optimale.',
        'benefits_en': 'Relieves stress, enhances mood, may help with mild pain and insomnia.',
        'benefits_fr': 'Soulage le stress, améliore l\'humeur, peut aider contre les douleurs légères et l\'insomnie.',
        'meta_description_en': 'Premium Apple Jack hybrid cannabis with sweet apple flavors and balanced effects.',
        'meta_keywords_en': 'apple jack, hybrid cannabis, premium weed, organic, thc',
    },
    {
        'slug': 'banana-kush',
        'category_slug': 'thc-flower',
        'name': 'Banana Kush',
        'name_en': 'Banana Kush',
        'name_fr': 'Banana Kush',
        'price': '250.00',
        'stock_quantity': 85,
        'is_active': True,
        'featured': True,
        'strain_type': 'Indica',
        'preferred_ratio': None,
        'recommended_methods': ['flower', 'edible'],
        'average_rating': '0.00',
        'rating_count': 0,
        'description_en': 'A potent indica strain with sweet banana aroma and deep relaxation effects.',
        'description_fr': 'Une puissante variété indica avec un arôme sucré de banane et des effets de relaxation profonde.',
        'composition_en': 'THC: 20-24%, CBD: <0.5%, Terpenes: Limonene, Myrcene, Linalool',
        'composition_fr': 'THC : 20-24 %, CBD : <0,5 %, Terpènes : Limonène, Myrcène, Linalol',
        'usage_instructions_en': 'Best for evening use. Start with small amounts. Smoke or vaporize.',
        'usage_instructions_fr': 'Idéal pour une utilisation en soirée. Commencez par de petites quantités. Fumez ou vaporisez.',
        'creation_method_en': 'Organic soil grown, hand-harvested, slow-dried to preserve terpenes.',
        'creation_method_fr': 'Cultivé en terreau biologique, récolté à la main, séché lentement pour préserver les terpènes.',
        'benefits_en': 'Promotes deep relaxation, helps with insomnia, may relieve muscle tension.',
        'benefits_fr': 'Favorise une relaxation profonde, aide contre l\'insomnie, peut soulager les tensions musculaires.',
        'meta_description_en': 'Premium Banana Kush indica with sweet tropical aroma and relaxing effects.',
        'meta_keywords_en': 'banana kush, indica, tropical strain, relaxing, thc',
    },
    {
        'slug': 'bio-jesus-hybrid-weed',
        'category_slug': 'thc-flower',
        'name': 'Bio-Jesus Hybrid Weed',
        'name_en': 'Bio-Jesus Hybrid Weed',
        'name_fr': 'Bio-Jesus Hybrid Weed',
        'price': '235.00',
        'stock_quantity': 60,
        'is_active': True,
        'featured': False,
        'strain_type': 'Hybrid',
        'preferred_ratio': 'balanced',
        'recommended_methods': ['flower', 'oil'],
        'average_rating': '0.00',
        'rating_count': 0,
        'description_en': 'A spiritual hybrid experience with earthy flavors and balanced effects.',
        'description_fr': 'Une expérience hybride spirituelle avec des saveurs terreuses et des effets équilibrés.',
        'composition_en': 'THC: 16-20%, CBD: 1-2%, Terpenes: Pinene, Humulene, Terpinolene',
        'composition_fr': 'THC : 16-20 %, CBD : 1-2 %, Terpènes : Pinène, Humulène, Terpinolène',
        'usage_instructions_en': 'Ideal for meditation or creative activities. Use moderately.',
        'usage_instructions_fr': 'Idéal pour la méditation ou les activités créatives. À utiliser avec modération.',
        'creation_method_en': 'Biodynamically grown, sun-cured, hand-processed with spiritual intention.',
        'creation_method_fr': 'Cultivé en biodynamie, séché au soleil, transformé à la main avec une intention spirituelle.',
        'benefits_en': 'Enhances mindfulness, promotes spiritual connection, may help with mild anxiety.',
        'benefits_fr': 'Améliore la pleine conscience, favorise la connexion spirituelle, peut aider contre l\'anxiété légère.',
        'meta_description_en': 'Bio-Jesus hybrid cannabis for spiritual experiences with earthy flavors.',
        'meta_keywords_en': 'bio jesus, hybrid, spiritual, earthy, thc',
    },
    # ── Medical / pharmaceutical products ────────────────────────────────────
    {
        'slug': 'advanced-pain-relief-formula',
        'category_slug': 'pain-relief',
        'name': 'Advanced Pain Relief Formula',
        'name_en': 'Advanced Pain Relief Formula',
        'name_fr': None,
        'price': '29.99',
        'stock_quantity': 150,
        'is_active': True,
        'featured': True,
        'strain_type': None,
        'preferred_ratio': None,
        'recommended_methods': None,
        'average_rating': '0.00',
        'rating_count': 0,
        'description_en': (
            'A comprehensive pain relief formula combining natural and synthetic compounds for '
            'effective pain management. Suitable for chronic pain conditions and acute injuries.'
        ),
        'description_fr': None,
        'composition_en': (
            'Active ingredients: Acetaminophen 500mg, Ibuprofen 200mg, Natural willow bark extract '
            '100mg. Inactive ingredients: Microcrystalline cellulose, magnesium stearate, silicon dioxide.'
        ),
        'composition_fr': None,
        'usage_instructions_en': (
            'Take 1-2 tablets every 6-8 hours as needed for pain. Do not exceed 6 tablets in 24 hours. '
            'Take with food to reduce stomach irritation. Consult healthcare provider for use beyond 10 days.'
        ),
        'usage_instructions_fr': None,
        'creation_method_en': (
            'Manufactured using pharmaceutical-grade equipment in GMP-certified facilities. Active '
            'ingredients are precisely measured and combined using advanced tablet compression technology.'
        ),
        'creation_method_fr': None,
        'benefits_en': (
            'Provides fast-acting pain relief, reduces inflammation, improves mobility, and enhances '
            'quality of life. Effective for headaches, muscle pain, joint pain, and minor injuries.'
        ),
        'benefits_fr': None,
        'meta_description_en': None,
        'meta_keywords_en': None,
    },
    {
        'slug': 'cardiosupport-plus',
        'category_slug': 'cardiovascular-health',
        'name': 'CardioSupport Plus',
        'name_en': 'CardioSupport Plus',
        'name_fr': None,
        'price': '45.50',
        'stock_quantity': 200,
        'is_active': True,
        'featured': True,
        'strain_type': None,
        'preferred_ratio': None,
        'recommended_methods': None,
        'average_rating': '0.00',
        'rating_count': 0,
        'description_en': (
            'Premium cardiovascular support supplement designed to promote heart health and maintain '
            'healthy blood pressure levels.'
        ),
        'description_fr': None,
        'composition_en': (
            'Coenzyme Q10 100mg, Omega-3 fatty acids 1000mg, Magnesium 200mg, Hawthorn extract 150mg, '
            'Garlic extract 100mg.'
        ),
        'composition_fr': None,
        'usage_instructions_en': (
            'Take 2 capsules daily with meals. For best results, take consistently at the same time '
            'each day. Consult physician before use if taking blood thinners.'
        ),
        'usage_instructions_fr': None,
        'creation_method_en': (
            'Cold-pressed extraction methods preserve active compounds. Encapsulated in vegetarian '
            'capsules using pharmaceutical-grade equipment.'
        ),
        'creation_method_fr': None,
        'benefits_en': (
            'Supports healthy cholesterol levels, promotes circulation, maintains blood pressure within '
            'normal range, and provides antioxidant protection for the cardiovascular system.'
        ),
        'benefits_fr': None,
        'meta_description_en': None,
        'meta_keywords_en': None,
    },
    {
        'slug': 'digestease-pro',
        'category_slug': 'digestive-health',
        'name': 'DigestEase Pro',
        'name_en': 'DigestEase Pro',
        'name_fr': None,
        'price': '32.75',
        'stock_quantity': 120,
        'is_active': True,
        'featured': False,
        'strain_type': None,
        'preferred_ratio': None,
        'recommended_methods': None,
        'average_rating': '0.00',
        'rating_count': 0,
        'description_en': 'Advanced digestive enzyme complex with probiotics to support optimal digestion and gut health.',
        'description_fr': None,
        'composition_en': (
            'Digestive enzyme blend 300mg (amylase, protease, lipase), Probiotic blend 10 billion CFU '
            '(Lactobacillus, Bifidobacterium), Prebiotic fiber 200mg.'
        ),
        'composition_fr': None,
        'usage_instructions_en': (
            'Take 1 capsule with each meal, up to 3 times daily. Store in cool, dry place. '
            'Refrigeration recommended after opening.'
        ),
        'usage_instructions_fr': None,
        'creation_method_en': (
            'Enzymes are derived from plant sources and stabilized using proprietary technology. '
            'Probiotics are freeze-dried to maintain viability.'
        ),
        'creation_method_fr': None,
        'benefits_en': (
            'Improves digestion, reduces bloating and gas, supports nutrient absorption, maintains '
            'healthy gut flora, and promotes regular bowel movements.'
        ),
        'benefits_fr': None,
        'meta_description_en': None,
        'meta_keywords_en': None,
    },
    {
        'slug': 'immunoshield-complex',
        'category_slug': 'immune-support',
        'name': 'ImmunoShield Complex',
        'name_en': 'ImmunoShield Complex',
        'name_fr': None,
        'price': '38.25',
        'stock_quantity': 180,
        'is_active': True,
        'featured': True,
        'strain_type': None,
        'preferred_ratio': None,
        'recommended_methods': None,
        'average_rating': '0.00',
        'rating_count': 0,
        'description_en': 'Comprehensive immune system support formula with vitamins, minerals, and herbal extracts.',
        'description_fr': None,
        'composition_en': (
            'Vitamin C 1000mg, Vitamin D3 2000IU, Zinc 15mg, Elderberry extract 300mg, Echinacea '
            'extract 200mg, Astragalus root 150mg.'
        ),
        'composition_fr': None,
        'usage_instructions_en': (
            'Take 2 tablets daily with food. During times of increased immune challenge, may increase '
            'to 3 tablets daily for up to 7 days.'
        ),
        'usage_instructions_fr': None,
        'creation_method_en': (
            'Standardized herbal extracts are combined with pharmaceutical-grade vitamins and minerals '
            'using advanced coating technology.'
        ),
        'creation_method_fr': None,
        'benefits_en': (
            'Strengthens immune system, reduces duration of seasonal challenges, provides antioxidant '
            'protection, and supports overall wellness.'
        ),
        'benefits_fr': None,
        'meta_description_en': None,
        'meta_keywords_en': None,
    },
    {
        'slug': 'respiclear-lung-support',
        'category_slug': 'respiratory-care',
        'name': 'RespiClear Lung Support',
        'name_en': 'RespiClear Lung Support',
        'name_fr': None,
        'price': '41.00',
        'stock_quantity': 95,
        'is_active': True,
        'featured': False,
        'strain_type': None,
        'preferred_ratio': None,
        'recommended_methods': None,
        'average_rating': '0.00',
        'rating_count': 0,
        'description_en': 'Natural respiratory support formula designed to promote clear breathing and lung health.',
        'description_fr': None,
        'composition_en': (
            'N-Acetyl Cysteine 600mg, Quercetin 250mg, Bromelain 200mg, Mullein leaf extract 150mg, '
            'Eucalyptus oil 50mg.'
        ),
        'composition_fr': None,
        'usage_instructions_en': (
            'Take 1-2 capsules twice daily between meals. Drink plenty of water. Not recommended for '
            'children under 12.'
        ),
        'usage_instructions_fr': None,
        'creation_method_en': (
            'Herbal extracts are standardized for active compounds and combined with amino acids using '
            'gentle processing methods.'
        ),
        'creation_method_fr': None,
        'benefits_en': (
            'Supports respiratory function, promotes clear airways, provides antioxidant protection for '
            'lung tissue, and helps maintain comfortable breathing.'
        ),
        'benefits_fr': None,
        'meta_description_en': None,
        'meta_keywords_en': None,
    },
    {
        'slug': 'joint-mobility-formula',
        'category_slug': 'pain-relief',
        'name': 'Joint Mobility Formula',
        'name_en': 'Joint Mobility Formula',
        'name_fr': None,
        'price': '52.99',
        'stock_quantity': 75,
        'is_active': True,
        'featured': True,
        'strain_type': None,
        'preferred_ratio': None,
        'recommended_methods': None,
        'average_rating': '0.00',
        'rating_count': 0,
        'description_en': (
            'Advanced joint support formula combining glucosamine, chondroitin, and anti-inflammatory compounds.'
        ),
        'description_fr': None,
        'composition_en': (
            'Glucosamine sulfate 1500mg, Chondroitin sulfate 1200mg, MSM 1000mg, Turmeric extract 500mg, '
            'Boswellia extract 300mg.'
        ),
        'composition_fr': None,
        'usage_instructions_en': (
            'Take 3 capsules daily with meals. Allow 4-6 weeks for optimal benefits. Continue use for '
            'sustained joint health.'
        ),
        'usage_instructions_fr': None,
        'creation_method_en': (
            'Pharmaceutical-grade ingredients are combined using advanced encapsulation technology to '
            'ensure stability and bioavailability.'
        ),
        'creation_method_fr': None,
        'benefits_en': (
            'Supports joint flexibility, reduces stiffness, promotes cartilage health, and helps maintain '
            'comfortable joint movement.'
        ),
        'benefits_fr': None,
        'meta_description_en': None,
        'meta_keywords_en': None,
    },
    {
        'slug': 'heart-rhythm-support',
        'category_slug': 'cardiovascular-health',
        'name': 'Heart Rhythm Support',
        'name_en': 'Heart Rhythm Support',
        'name_fr': None,
        'price': '48.75',
        'stock_quantity': 110,
        'is_active': True,
        'featured': False,
        'strain_type': None,
        'preferred_ratio': None,
        'recommended_methods': None,
        'average_rating': '0.00',
        'rating_count': 0,
        'description_en': 'Specialized formula to support healthy heart rhythm and electrical conduction.',
        'description_fr': None,
        'composition_en': (
            'Magnesium glycinate 400mg, Potassium citrate 300mg, Taurine 500mg, L-Carnitine 250mg, '
            'Hawthorn berry 200mg.'
        ),
        'composition_fr': None,
        'usage_instructions_en': (
            'Take 2 capsules daily, preferably with evening meal. Monitor heart rate if taking cardiac medications.'
        ),
        'usage_instructions_fr': None,
        'creation_method_en': (
            'Chelated minerals are combined with amino acids using pharmaceutical manufacturing standards.'
        ),
        'creation_method_fr': None,
        'benefits_en': (
            'Supports healthy heart rhythm, promotes electrical stability, maintains mineral balance, '
            'and supports overall cardiac function.'
        ),
        'benefits_fr': None,
        'meta_description_en': None,
        'meta_keywords_en': None,
    },
    {
        'slug': 'probiotic-defense',
        'category_slug': 'digestive-health',
        'name': 'Probiotic Defense',
        'name_en': 'Probiotic Defense',
        'name_fr': None,
        'price': '35.50',
        'stock_quantity': 160,
        'is_active': True,
        'featured': True,
        'strain_type': None,
        'preferred_ratio': None,
        'recommended_methods': None,
        'average_rating': '0.00',
        'rating_count': 0,
        'description_en': (
            'High-potency probiotic formula with multiple strains for comprehensive digestive and '
            'immune support.'
        ),
        'description_fr': None,
        'composition_en': (
            '50 billion CFU multi-strain blend: Lactobacillus acidophilus, L. rhamnosus, L. casei, '
            'Bifidobacterium longum, B. bifidum, Saccharomyces boulardii.'
        ),
        'composition_fr': None,
        'usage_instructions_en': (
            'Take 1 capsule daily on empty stomach or as directed by healthcare provider. Refrigerate '
            'after opening.'
        ),
        'usage_instructions_fr': None,
        'creation_method_en': (
            'Probiotics are freeze-dried using proprietary technology and encapsulated in acid-resistant capsules.'
        ),
        'creation_method_fr': None,
        'benefits_en': (
            'Restores healthy gut flora, supports digestive health, enhances immune function, and '
            'promotes nutrient absorption.'
        ),
        'benefits_fr': None,
        'meta_description_en': None,
        'meta_keywords_en': None,
    },
    {
        'slug': 'antioxidant-shield',
        'category_slug': 'immune-support',
        'name': 'Antioxidant Shield',
        'name_en': 'Antioxidant Shield',
        'name_fr': None,
        'price': '42.25',
        'stock_quantity': 140,
        'is_active': True,
        'featured': False,
        'strain_type': None,
        'preferred_ratio': None,
        'recommended_methods': None,
        'average_rating': '0.00',
        'rating_count': 0,
        'description_en': (
            'Powerful antioxidant complex to protect against free radical damage and support cellular health.'
        ),
        'description_fr': None,
        'composition_en': (
            'Alpha-lipoic acid 300mg, Resveratrol 200mg, Green tea extract 150mg, Grape seed extract '
            '100mg, Selenium 200mcg.'
        ),
        'composition_fr': None,
        'usage_instructions_en': (
            'Take 1-2 capsules daily with meals. Best taken with healthy fats for optimal absorption.'
        ),
        'usage_instructions_fr': None,
        'creation_method_en': (
            'Antioxidants are extracted using CO2 methods to preserve potency and combined in '
            'light-resistant capsules.'
        ),
        'creation_method_fr': None,
        'benefits_en': (
            'Provides cellular protection, supports healthy aging, enhances immune function, and '
            'promotes cardiovascular health.'
        ),
        'benefits_fr': None,
        'meta_description_en': None,
        'meta_keywords_en': None,
    },
    {
        'slug': 'bronchial-comfort',
        'category_slug': 'respiratory-care',
        'name': 'Bronchial Comfort',
        'name_en': 'Bronchial Comfort',
        'name_fr': None,
        'price': '36.99',
        'stock_quantity': 85,
        'is_active': True,
        'featured': False,
        'strain_type': None,
        'preferred_ratio': None,
        'recommended_methods': None,
        'average_rating': '0.00',
        'rating_count': 0,
        'description_en': (
            'Soothing respiratory formula with herbs traditionally used to support bronchial comfort.'
        ),
        'description_fr': None,
        'composition_en': (
            'Ivy leaf extract 300mg, Thyme extract 200mg, Marshmallow root 150mg, Licorice root 100mg, '
            'Menthol 25mg.'
        ),
        'composition_fr': None,
        'usage_instructions_en': (
            'Take 1 capsule 2-3 times daily. May be taken with warm water or herbal tea for enhanced comfort.'
        ),
        'usage_instructions_fr': None,
        'creation_method_en': (
            'Traditional herbal extracts are standardized and combined using gentle processing to '
            'maintain therapeutic properties.'
        ),
        'creation_method_fr': None,
        'benefits_en': (
            'Soothes respiratory passages, supports comfortable breathing, provides natural expectorant '
            'action, and promotes respiratory comfort.'
        ),
        'benefits_fr': None,
        'meta_description_en': None,
        'meta_keywords_en': None,
    },
]


class Command(BaseCommand):
    help = 'Populate database from original SQLite data (idempotent — safe to run repeatedly)'

    def handle(self, *args, **options):
        self.stdout.write('Creating categories...')
        cat_count = self._create_categories()
        self.stdout.write(self.style.SUCCESS(f'Created {cat_count} categories'))

        self.stdout.write('Creating products...')
        prod_count = self._create_products()
        self.stdout.write(self.style.SUCCESS(f'Created {prod_count} products'))

        self.stdout.write('Creating site settings...')
        self._create_site_settings()
        self.stdout.write(self.style.SUCCESS('Done'))

        self.stdout.write(self.style.SUCCESS('Database populated successfully.'))

    # ------------------------------------------------------------------
    def _create_categories(self):
        created_count = 0
        for data in CATEGORIES:
            slug = data['slug']
            defaults = {k: v for k, v in data.items() if k != 'slug'}
            _, created = Category.objects.update_or_create(slug=slug, defaults=defaults)
            if created:
                self.stdout.write(f'  Created: {data["name_en"]}')
                created_count += 1
            else:
                self.stdout.write(f'  Skipped existing: {data["name_en"]}')
        return created_count

    @staticmethod
    def _truncate(value, max_len=160):
        if value and len(value) > max_len:
            return value[:max_len - 3] + '...'
        return value

    def _create_products(self):
        # Pre-load category map (slug → instance) so we don't hit DB per product
        cat_map = {c.slug: c for c in Category.objects.all()}
        created_count = 0

        for data in PRODUCTS:
            slug = data['slug']
            cat_slug = data['category_slug']
            category = cat_map.get(cat_slug)
            if category is None:
                self.stdout.write(
                    self.style.WARNING(f'  Skipping {slug}: category "{cat_slug}" not found')
                )
                continue

            defaults = {k: v for k, v in data.items() if k not in ('slug', 'category_slug')}
            defaults['category'] = category
            defaults['image'] = ''  # images uploaded manually via admin to Cloudinary

            # PostgreSQL enforces max_length=160 on meta_description fields
            for field in ('meta_description', 'meta_description_en', 'meta_description_fr'):
                if defaults.get(field):
                    defaults[field] = self._truncate(defaults[field], 160)

            _, created = Product.objects.update_or_create(slug=slug, defaults=defaults)
            if created:
                self.stdout.write(f'  Created: {data["name_en"]}')
                created_count += 1
            else:
                self.stdout.write(f'  Skipped existing: {data["name_en"]}')

        return created_count

    def _create_site_settings(self):
        obj, created = SiteSettings.objects.update_or_create(
            pk=1,
            defaults={
                'site_name': 'Green Houses CBD',
                'site_name_en': 'Green Houses CBD',
                'site_name_fr': 'GreenMed Store',
                'tagline': 'Premium Natural Medical Products',
                'tagline_en': 'Premium Natural Medical Products',
                'tagline_fr': 'Premium Natural Medical Products',
                'email': 'info@greenhousescbd.com',
                'phone': '+33 1 23 45 67 89',
                'address': 'Paris, France',
                'address_en': 'Paris, France',
                'address_fr': 'Paris, France',
                'business_hours': 'Mon-Fri: 9:00-18:00\nSat: 10:00-16:00\nSun: Closed',
                'business_hours_en': 'Mon-Fri: 9:00-18:00\nSat: 10:00-16:00\nSun: Closed',
                'business_hours_fr': 'Mon-Fri: 9:00-18:00\nSat: 10:00-16:00\nSun: Closed',
                'about_text': 'We specialize in premium natural medical products derived from organic sources.',
                'about_text_en': 'We specialize in premium natural medical products derived from organic sources.',
                'about_text_fr': 'We specialize in premium natural medical products derived from organic sources.',
                'facebook_url': '',
                'twitter_url': '',
                'instagram_url': '',
                'privacy_policy': '',
                'terms_of_service': '',
                'bank_name': '',
                'bank_account_name': '',
                'bank_account_number': '',
                'bank_iban': '',
                'bank_swift_bic': '',
            },
        )
        action = 'Created' if created else 'Updated'
        self.stdout.write(f'  {action}: SiteSettings (pk=1)')
