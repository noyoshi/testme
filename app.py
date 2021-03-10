from git import Repo

repo = Repo(".", search_parent_directories=True)
print(repo.__dir__())
print(repo.commit("HEAD"))
