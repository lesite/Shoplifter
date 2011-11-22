# encoding: utf-8

import mongoengine as db

from nose.tools import *

from shoplifter.catalog.taxonomy.model import Taxonomy
from shoplifter.catalog.product.model import Product
from ludibrio import Stub

db.connect('shoplifter_test')


with Stub() as get_lang:
    from shoplifter.core.db.field import get_lang
    get_lang() >> [u'en', u'se', u'eg']
    

def _create_products():

	men = Taxonomy(name={'en': 'men'})
	men.save()
	women = Taxonomy(name={'en': 'women'})
	women.save()
	m_pants = Taxonomy(name={'en': 'Pants'}, parent=men)
	m_pants.save()
	m_tops = Taxonomy(name={'en': 'tops'}, parent=men)
	m_tops.save()
	w_pants = Taxonomy(name={'en': 'Pants'}, parent=women)
	w_pants.save()
	w_tops = Taxonomy(name={'en': 'tops'}, parent=women)
	w_tops.save()
	sales = Taxonomy(name={'en': 'sales'})
	sales.save()

	Product(code='mpants', name='man\'s pants', slug='pants',
			taxonomies=[m_pants,]).save()
	Product(code='mtops', name='man\'s tops', slug='tops',
			taxonomies=[m_tops,]).save()
	Product(code='mpants-sale', name='man\'s pants on sale',
			slug='men-pants-sale', taxonomies=[m_pants, sales]).save()
	Product(code='mtops-sale', name='man\'s tops on sale',
			slug='men-tops-sale', taxonomies=[m_tops, sales]).save()

	Product(code='wpants', name='women\'s pants', slug='women-pants',
			taxonomies=[w_pants,]).save()
	Product(code='wtops', name='women\'s tops', slug='women-tops',
			taxonomies=[w_tops,]).save()
	Product(code='wpants-sale', name='women\'s pants on sale',
			slug='women-pants-sale', taxonomies=[w_pants, sales]).save()
	Product(code='wtops-sale', name='women\'s tops on sale',
			slug='women-tops-sale', taxonomies=[w_tops, sales]).save()


def setup():
	Product.drop_collection()
	Taxonomy.drop_collection()
	_create_products()


class TestTaxonomySpec(object):
	def setup(self):
		self.men = Taxonomy.objects.get(path=u'/men')
		self.women = Taxonomy.objects.get(path=u'/women')
		self.sales = Taxonomy.objects.get(path=u'/sales')

	def teardown(self):
		pass

	def test_simple_taxonomy(self):
		from mongoengine.document import OperationError
		pants = Taxonomy.objects(name__en__iexact='pants')

		assert_true(pants.count(), 2)
		assert_true(pants[0].path != pants[1].path)
		assert_true(pants[0].parent != pants[1].parent)
		pants2 = Taxonomy(name={'en': 'Pants'}, parent=self.men)
		assert_raises(OperationError, pants2.save)

	def test_multiple_taxonomies(self):
		children = Taxonomy.objects.filter(parent=self.men)
		assert_true(children.count(), 2)

	def test_union_taxonomies(self):
		prods = Product.objects(self.men | self.women)
		assert_equal(prods.count(), 8)

	def test_intersect_taxonomies(self):
		men = set(Product.objects(taxonomies__in=self.men.descendants))
		women = set(Product.objects(taxonomies__in=self.women.descendants))
		sales = set(Product.objects(taxonomies__in=self.sales.descendants))
		no_prods = Product.objects(self.men & self.women)
		men_sales = Product.objects(self.men & self.sales)

		assert_equal(len(men & women), no_prods.count())
		assert_equal(len(men & sales), men_sales.count())
		assert_equal(len(men_sales), 2)

	def test_substraction_taxonomies(self):
		men = set(Product.objects(taxonomies__in=self.men.descendants))
		sales = set(Product.objects(taxonomies__in=self.sales.descendants))
		mens_no_sale = Product.objects(self.men - self.sales)
		assert_equal(len(men - sales), 2)
		assert_equal(mens_no_sale.count(), 2)
		assert_equal((set(mens_no_sale) & (men - sales)), set(mens_no_sale))
		assert_true(not set(self.sales).intersection(mens_no_sale[0].taxonomies))