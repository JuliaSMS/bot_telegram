try:
    import aiogram
    print('aiogram OK', getattr(aiogram, '__version__', 'unknown'))
except Exception as e:
    print('aiogram import failed:', e)
