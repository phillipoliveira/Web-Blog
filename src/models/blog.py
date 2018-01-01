import uuid
import datetime
from src.common.database import Database
from src.models.post import Post


class Blog(object):
    def __init__(self, author, title, description, author_id, _id=None):
        self.author = author
        self.author_id = author_id
        self.title = title
        self.description = description
        self._id = uuid.uuid4().hex if _id is None else _id

    def new_post(self, title, content, date=datetime.datetime.utcnow()):
        post = Post(blog_id=self._id,
                    title=title,
                    content=content,
                    author=self.author,
                    created_date=date)
        post.save_to_mongo()
        # Author of the blog is the author of the posts,
        # id of the blog is automatically set as the post's
        # blog_id

    def get_posts(self):
        return Post.from_blog(self._id)

    def save_to_mongo(self):
        Database.insert(collection='blogs', data=self.json())

    def json(self):
        return {
            'author': self.author,
            'author_id': self.author_id,
            'title': self.title,
            'description': self.description,
            '_id': self._id
        }

    @classmethod
    def from_mongo(cls, id):
        blog_data = Database.find_one(collection='blogs',
                                      query={'_id': id})
        return cls(**blog_data)
    # We've written this this way, so that we can later run
    # methods on the blog object we've returned.
    # @classmethod allows us to use 'cls' to return the class
    # we're currently working with, in case the class name ever
    # changes.

    @classmethod
    def find_by_author_id(cls, author_id):
        blogs = Database.find(collection="blogs",
                              query={"author_id": author_id})
        return [cls(**blog) for blog in blogs]
        # This will return blog objects in a list, using list comprehension.

    @property
    def id(self):
        return self._id
