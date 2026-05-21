pipeline {
    agent any

    environment {
        IMAGE_NAME = 'fittrack-gym-app'
        IMAGE_TAG  = "v${BUILD_NUMBER}"
        CONTAINER  = 'fittrack-app'
        PORT       = '5000'
    }

    stages {

        stage('Checkout') {
            steps {
                echo '📥 Cloning repository from Git...'
                checkout scm
            }
        }

        stage('Install Dependencies') {
            steps {
                echo '📦 Installing Python dependencies...'
                sh '''
                    python3 -m venv venv
                    . venv/bin/activate
                    pip install --upgrade pip
                    pip install -r requirements.txt
                '''
            }
        }

        stage('Run Tests') {
            steps {
                echo '🧪 Running application tests...'
                sh '''
                    . venv/bin/activate
                    python -c "from app import app, init_db; init_db(); print('✅ App imports OK')"
                    python -c "
from app import app, init_db
init_db()
client = app.test_client()
res = client.get('/')
assert res.status_code == 200, 'Dashboard failed'
res2 = client.get('/members')
assert res2.status_code == 200, 'Members page failed'
res3 = client.get('/attendance')
assert res3.status_code == 200, 'Attendance page failed'
res4 = client.get('/payments')
assert res4.status_code == 200, 'Payments page failed'
print('✅ All route tests passed!')
"
                '''
            }
        }

        stage('Build Docker Image') {
            steps {
                echo "🐳 Building Docker image: ${IMAGE_NAME}:${IMAGE_TAG}"
                sh "docker build -t ${IMAGE_NAME}:${IMAGE_TAG} ."
                sh "docker tag ${IMAGE_NAME}:${IMAGE_TAG} ${IMAGE_NAME}:latest"
            }
        }

        stage('Stop Old Container') {
            steps {
                echo '🛑 Stopping existing container (if any)...'
                sh """
                    docker stop ${CONTAINER} || true
                    docker rm   ${CONTAINER} || true
                """
            }
        }

        stage('Deploy Container') {
            steps {
                echo "🚀 Deploying ${IMAGE_NAME}:${IMAGE_TAG}..."
                sh """
                    docker run -d \
                        --name ${CONTAINER} \
                        -p ${PORT}:5000 \
                        --restart unless-stopped \
                        ${IMAGE_NAME}:${IMAGE_TAG}
                """
            }
        }

        stage('Health Check') {
            steps {
                echo '❤️ Running health check...'
                sh '''
                    sleep 5
                    STATUS=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:5000/)
                    if [ "$STATUS" -eq 200 ]; then
                        echo "✅ Health check passed — App is live on port 5000!"
                    else
                        echo "❌ Health check failed — HTTP $STATUS"
                        exit 1
                    fi
                '''
            }
        }

    }

    post {
        success {
            echo """
            ╔══════════════════════════════════════╗
            ║   ✅ BUILD & DEPLOY SUCCESSFUL!      ║
            ║   FitTrack is live on port 5000      ║
            ╚══════════════════════════════════════╝
            """
        }
        failure {
            echo '❌ Pipeline failed. Check logs above.'
            sh "docker stop ${CONTAINER} || true"
        }
        always {
            echo "🧹 Build #${BUILD_NUMBER} complete."
        }
    }
}
