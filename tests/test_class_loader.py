from profit_analyzer.utils.class_loader import discover_classes, initialize_from_config

def test_discover_classes():
    cmap = discover_classes('profit_analyzer')
    assert 'FileLoader' in cmap
    assert 'ProfitCalculator' in cmap

def test_initialize(tmp_path):
    cfg = {
        'modules':[
            {'class':'FileLoader','args':{'folder_path':'.','include_patterns':['*.md']}},
        ]
    }
    loaded_config = initialize_from_config(cfg, 'profit_analyzer')
    assert loaded_config['modules'][0].__class__.__name__ == 'FileLoader'
