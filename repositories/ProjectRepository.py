from models.Project import Project
from typing import List


class ProjectRepository:
    def __init__(self, db):
        self.db = db

    async def create(self, project: Project) -> int:
        query = """
        INSERT INTO projects (name, user_id, description, documents, photos, links)
        VALUES (%s, %s, %s, %s, %s, %s)
        """
        values = (
            project.name,
            project.user_id,
            project.description,
            ','.join(project.documents) if project.documents else None,
            ','.join(project.photos) if project.photos else None,
            ','.join(project.links) if project.links else None
        )

        print(values)
        print(type(values))
        print("Printing values and queries")

        await self.db.execute(query, values)
        return self.db.lastrowid

    async def get_by_id(self, project_id: int) -> Project:
        query = "SELECT * FROM projects WHERE id = %s"
        await self.db.execute(query, (project_id,))
        result = await self.db.fetchone()
        if result:
            return Project(**result)
        return None

    async def get_all(self) -> List[Project]:
        query = "SELECT * FROM projects"
        await self.db.execute(query)
        results = await self.db.fetchall()
        return [Project(**row) for row in results]

    async def update(self, project: Project) -> bool:
        query = """
        UPDATE projects
        SET name = %s, user_id = %s, description = %s, documents = %s, photos = %s, links = %s
        WHERE id = %s
        """
        values = (
            project.name,
            project.user_id,
            project.description,
            ','.join(project.documents) if project.documents else None,
            ','.join(project.photos) if project.photos else None,
            ','.join(project.links) if project.links else None,
            project.id
        )
        await self.db.execute(query, values)
        return self.db.rowcount > 0

    async def delete(self, project_id: int) -> bool:
        query = "DELETE FROM projects WHERE id = %s"
        await self.db.execute(query, (project_id,))
        return self.db.rowcount > 0
