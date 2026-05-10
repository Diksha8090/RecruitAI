import sys
sys.path.insert(0, r'c:\Users\abhir\Downloads\AI Resume Screening Tool (1)\AI Resume Screening Tool\backend')
from app import create_app

app = create_app()
with app.app_context():
    print('Registered blueprints:', list(app.blueprints.keys()))
    print('\nRegistered routes:')
    for rule in app.url_map.iter_rules():
        if 'static' not in rule.rule:
            print(f'  {rule.rule} -> {rule.endpoint} [{", ".join(sorted(rule.methods - {"HEAD", "OPTIONS"}))}]')
