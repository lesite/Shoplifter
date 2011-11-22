# encoding: utf-8

import operator

import mongoengine as db

from shoplifter.core import util
from shoplifter.core.db.field import TranslatedStringField


class Taxonomy(db.Document):
	""" The model will help the categorization of products

	The taxonomy can up and down using it's self as a reference point
	Using set theory we could create a new set of products
	(pants | tops) we want products that either pants or tops
	(pants & sale) we want products that are pants and on sale
	(pants - sale) we want products that are pants and not on sale
	"""

	id = db.ObjectIdField('_id')
	name = TranslatedStringField(required=True)
	description = TranslatedStringField()

	path = db.StringField(unique=True)
	parent = db.ReferenceField('self')
	parents = db.ListField(db.ReferenceField('self'), default=list)

	# @property
	# def children(self):
	# 	return Taxonomy.objects(parent=self)
	
	@property
	def descendants(self):
		return Taxonomy.objects(path__startswith=self.path)

	@classmethod
	def pre_save(cls, sender, document, **kwargs):
		slug = util.slugify(document.name['en'], limit=30)

		# TODO:
		# If name is dirty, update path of all descendants!

		if document.parent:
			document.parents = document.parent.parents + [document.parent]
			document.path = document.parent.path + u'/' + slug

		else:
			document.parents = []
			document.path = u'/' + slug
	
	def __repr__(self):
		return '<Taxonomy {} "{}">'.format(self.path, self.name)

	def __or__(self, other):
		taxonomies = ([self] + list(self.descendants.only('id')) + [other]
				+ list(other.descendants.only('id')))
		return db.Q(taxonomies__in=taxonomies)


	def __and__(self, other):
		"""Return query components that find products contained in both self
		and another taxonomy.
		
		For example:
			
			pants = Taxonomy(name="Pants")
			sale = Taxonomy(name="Sale")

			pants & sale
		"""
		ours = list(self.descendants)
		theirs = list(other.descendants)

		query = db.Q(taxonomies__in=ours) & db.Q(taxonomies__not__nin=theirs)
		return query
	
	def __sub__(self, other):
		ours = list(self.descendants)
		theirs = list(other.descendants)

		query = db.Q(taxonomies__in=ours) & db.Q(taxonomies__nin=theirs)
		return query

db.signals.pre_save.connect(Taxonomy.pre_save, sender=Taxonomy)