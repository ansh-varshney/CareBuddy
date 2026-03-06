pipeline {
    agent any

    tools {
        nodejs 'NodeJS-20'
    }

    environment {
        DOCKER_REGISTRY = 'your-dockerhub-username'
        IMAGE_TAG        = "${env.BUILD_NUMBER}"
        BACKEND_IMAGE    = "${DOCKER_REGISTRY}/carebuddy-backend:${IMAGE_TAG}"
        FRONTEND_IMAGE   = "${DOCKER_REGISTRY}/carebuddy-frontend:${IMAGE_TAG}"
        // Ensure pip3 / python3 are on PATH in Jenkins container
        PATH             = "/usr/bin:/usr/local/bin:${env.PATH}"
    }

    stages {

        // ── 0. Install Python (Jenkins container needs it) ────────
        stage('Setup Python') {
            steps {
                sh '''
                    python3 --version
                    python3 -m venv /var/jenkins_home/.ci-venv
                    /var/jenkins_home/.ci-venv/bin/pip install --quiet --upgrade pip
                '''
            }
        }

        // ── 1. Checkout ───────────────────────────────────────────
        stage('Checkout') {

            steps {
                checkout scm
                echo "✅ Checked out branch: ${env.BRANCH_NAME} (build #${env.BUILD_NUMBER})"
            }
        }

        // ── 2. Lint Backend ───────────────────────────────────────
        stage('Backend Lint') {
            steps {
                dir('backend') {
                    sh '''
                        /var/jenkins_home/.ci-venv/bin/pip install --quiet ruff
                        /var/jenkins_home/.ci-venv/bin/ruff check . --output-format=github
                    '''
                }
            }
        }

        // ── 3. Lint Frontend ──────────────────────────────────────
        stage('Frontend Lint') {
            steps {
                dir('frontend') {
                    sh '''
                        npm ci --silent
                        npx ng lint --format stylish
                    '''
                }
            }
        }

        // ── 4. Backend Tests ──────────────────────────────────────
        stage('Backend Tests') {
            steps {
                dir('backend') {
                    sh '''
                        /var/jenkins_home/.ci-venv/bin/pip install --quiet -r requirements.txt -r requirements-test.txt
                        mkdir -p reports
                        /var/jenkins_home/.ci-venv/bin/pytest tests/ \
                            --junitxml=reports/test-results.xml \
                            --cov=app \
                            --cov-report=xml:reports/coverage.xml \
                            --cov-report=term-missing \
                            -q
                    '''
                }
            }
            post {
                always {
                    junit 'backend/reports/test-results.xml'
                }
            }
        }

        // ── 5. Frontend Tests ─────────────────────────────────────
        stage('Frontend Tests') {
            steps {
                dir('frontend') {
                    sh 'npx ng test --watch=false --browsers=ChromeHeadless --code-coverage'
                }
            }
        }

        // ── 6. Security Scan (parallel) ───────────────────────────
        stage('Security Scan') {
            parallel {
                stage('Python Audit') {
                    steps {
                        dir('backend') {
                            sh '''
                                /var/jenkins_home/.ci-venv/bin/pip install --quiet pip-audit
                                /var/jenkins_home/.ci-venv/bin/pip-audit -r requirements.txt || true
                            '''
                        }
                    }
                }
                stage('NPM Audit') {
                    steps {
                        dir('frontend') {
                            sh 'npm audit --audit-level=high || true'
                        }
                    }
                }
            }
        }

        // ── 7. Build Docker Images ────────────────────────────────
        stage('Build Docker Images') {
            steps {
                sh "docker build -t ${BACKEND_IMAGE}  ./backend"
                sh "docker build -t ${FRONTEND_IMAGE} ./frontend"
                echo "✅ Images built: ${BACKEND_IMAGE}, ${FRONTEND_IMAGE}"
            }
        }

        // ── 8. Push to Registry (main branch only) ────────────────
        stage('Push to Registry') {
            when { branch 'main' }
            steps {
                withCredentials([usernamePassword(
                    credentialsId: 'dockerhub-creds',
                    usernameVariable: 'DOCKER_USER',
                    passwordVariable: 'DOCKER_PASS'
                )]) {
                    sh '''
                        echo "$DOCKER_PASS" | docker login -u "$DOCKER_USER" --password-stdin
                        docker push ${BACKEND_IMAGE}
                        docker push ${FRONTEND_IMAGE}
                    '''
                }
            }
        }

        // ── 9. Deploy (main branch only) ──────────────────────────
        stage('Deploy') {
            when { branch 'main' }
            steps {
                sh '''
                    docker compose -f docker-compose.yml pull
                    docker compose -f docker-compose.yml up -d --remove-orphans
                '''
                echo "🚀 Deployed build #${IMAGE_TAG} to production"
            }
        }
    }

    post {
        always {
            cleanWs()
        }
        success {
            echo '✅ Pipeline PASSED — CareBuddy is healthy!'
        }
        failure {
            echo '❌ Pipeline FAILED — check logs above'
        }
    }
}
