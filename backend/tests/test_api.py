"""Tests for the API endpoints."""

from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


class TestHealthEndpoint:
    def test_health_check(self):
        response = client.get('/health')
        assert response.status_code == 200
        data = response.json()
        assert data['status'] == 'ok'


class TestPlatformsEndpoint:
    def test_list_platforms(self):
        response = client.get('/api/v1/platforms')
        assert response.status_code == 200
        data = response.json()
        ids = [p['id'] for p in data]
        assert 'wechat' in ids
        assert 'zhihu' in ids
        assert 'xiaohongshu' in ids
        assert 'bilibili' in ids
        # Plugin platforms auto-discovered from backend/plugins/
        assert len(data) >= 4


class TestPreviewEndpoint:
    def test_single_preview(self):
        response = client.post('/api/v1/preview/wechat', json={
            'content': '# Hello\n\n**Bold** text.',
            'title': 'Test',
        })
        assert response.status_code == 200
        data = response.json()
        assert data['platform_id'] == 'wechat'
        assert len(data['html']) > 0
        assert isinstance(data['warnings'], list)

    def test_batch_preview(self):
        response = client.post('/api/v1/preview/batch', json={
            'content': '# Test\n\nParagraph.',
            'platforms': ['wechat', 'zhihu'],
        })
        assert response.status_code == 200
        data = response.json()
        assert len(data['previews']) == 2

    def test_preview_invalid_platform(self):
        response = client.post('/api/v1/preview/nonexistent', json={
            'content': 'test',
        })
        assert response.status_code == 404


class TestPublishEndpoint:
    def test_simulated_publish(self):
        response = client.post('/api/v1/publish', json={
            'content': '# Test\n\nHello world.',
            'title': 'Test Article',
            'platforms': ['wechat', 'zhihu'],
        })
        assert response.status_code == 200
        data = response.json()
        assert data['total_platforms'] == 2
        assert data['successful'] == 2
        assert data['failed'] == 0

    def test_publish_no_platforms(self):
        response = client.post('/api/v1/publish', json={
            'content': 'test',
            'title': 'test',
            'platforms': [],
        })
        assert response.status_code == 400


class TestArticlesEndpoint:
    def test_create_and_get_article(self):
        # Create
        response = client.post('/api/v1/articles', json={
            'title': 'Test Article',
            'content': '# Hello\n\nWorld.',
            'tags': ['test'],
        })
        assert response.status_code == 201
        data = response.json()
        article_id = data['id']
        assert data['title'] == 'Test Article'

        # Get
        response = client.get(f'/api/v1/articles/{article_id}')
        assert response.status_code == 200
        assert response.json()['title'] == 'Test Article'

        # List
        response = client.get('/api/v1/articles')
        assert response.status_code == 200
        assert len(response.json()) >= 1

        # Delete
        response = client.delete(f'/api/v1/articles/{article_id}')
        assert response.status_code == 200

        # Verify deleted
        response = client.get(f'/api/v1/articles/{article_id}')
        assert response.status_code == 404

    def test_update_article(self):
        # Create
        response = client.post('/api/v1/articles', json={
            'title': 'Original',
            'content': 'Original content.',
        })
        article_id = response.json()['id']

        # Update
        response = client.put(f'/api/v1/articles/{article_id}', json={
            'title': 'Updated Title',
        })
        assert response.status_code == 200
        assert response.json()['title'] == 'Updated Title'

        # Cleanup
        client.delete(f'/api/v1/articles/{article_id}')

    def test_get_nonexistent_article(self):
        response = client.get('/api/v1/articles/nonexistent')
        assert response.status_code == 404
