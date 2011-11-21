from shoplifter.catalog.product.model import Product, Variant


def create_model(cls, save=True, force_insert=False, **kwargs):
    opts = getattr(cls, '_test_defaults', {})
    opts.update(kwargs)
    i = cls(**opts)
    if save:
        i.save(force_insert=force_insert)
    return i


def create_product(*args, **kwargs):
    return create_model(Product, *args, **kwargs)


def create_variant(*args, **kwargs):
    return create_model(Variant, *args, **kwargs)
