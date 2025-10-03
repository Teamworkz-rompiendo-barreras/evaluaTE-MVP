#!/usr/bin/env node

/**
 * Script para probar la configuración de CORS del backend
 * Verifica que el backend responda correctamente a las solicitudes CORS
 */

const https = require('https');
const http = require('http');

// URLs de prueba
const BACKEND_URL = 'https://evaluador-backend-fzbhemgtetfeeme6.spaincentral-01.azurewebsites.net';
const FRONTEND_URL = 'https://evaluador-frontend-fzbhemgtetfeeme6.spaincentral-01.azurestaticapps.net';

console.log('=== Prueba de Configuración CORS ===\n');

// Función para hacer solicitudes HTTP/HTTPS
function makeRequest(url, options = {}) {
    return new Promise((resolve, reject) => {
        const isHttps = url.startsWith('https');
        const client = isHttps ? https : http;
        
        const requestOptions = {
            method: options.method || 'GET',
            headers: {
                'Origin': FRONTEND_URL,
                'Access-Control-Request-Method': 'POST',
                'Access-Control-Request-Headers': 'Content-Type',
                'Content-Type': 'application/json',
                ...options.headers
            },
            timeout: 10000
        };

        const req = client.request(url, requestOptions, (res) => {
            let data = '';
            res.on('data', chunk => data += chunk);
            res.on('end', () => {
                resolve({
                    statusCode: res.statusCode,
                    headers: res.headers,
                    data: data
                });
            });
        });

        req.on('error', reject);
        req.on('timeout', () => reject(new Error('Timeout')));
        
        if (options.body) {
            req.write(options.body);
        }
        
        req.end();
    });
}

// Prueba 1: Health check básico
async function testHealthCheck() {
    console.log('1. Probando health check...');
    try {
        const response = await makeRequest(`${BACKEND_URL}/health`);
        console.log(`   Status: ${response.statusCode}`);
        console.log(`   CORS Headers:`, {
            'Access-Control-Allow-Origin': response.headers['access-control-allow-origin'],
            'Access-Control-Allow-Methods': response.headers['access-control-allow-methods'],
            'Access-Control-Allow-Headers': response.headers['access-control-allow-headers']
        });
        console.log(`   Response: ${response.data}\n`);
        return response.statusCode === 200;
    } catch (error) {
        console.log(`   Error: ${error.message}\n`);
        return false;
    }
}

// Prueba 2: OPTIONS preflight request
async function testPreflightRequest() {
    console.log('2. Probando solicitud preflight OPTIONS...');
    try {
        const response = await makeRequest(`${BACKEND_URL}/api/informe-ia`, {
            method: 'OPTIONS'
        });
        console.log(`   Status: ${response.statusCode}`);
        console.log(`   CORS Headers:`, {
            'Access-Control-Allow-Origin': response.headers['access-control-allow-origin'],
            'Access-Control-Allow-Methods': response.headers['access-control-allow-methods'],
            'Access-Control-Allow-Headers': response.headers['access-control-allow-headers'],
            'Access-Control-Allow-Credentials': response.headers['access-control-allow-credentials']
        });
        console.log(`   Response: ${response.data}\n`);
        return response.statusCode === 200 || response.statusCode === 204;
    } catch (error) {
        console.log(`   Error: ${error.message}\n`);
        return false;
    }
}

// Prueba 3: POST request real
async function testPostRequest() {
    console.log('3. Probando solicitud POST real...');
    try {
        const testPayload = {
            "candidate": "Juan Pérez",
            "position": "Desarrollador Frontend",
            "experience": "3 años",
            "skills": ["React", "JavaScript", "CSS"]
        };
        
        const response = await makeRequest(`${BACKEND_URL}/api/informe-ia`, {
            method: 'POST',
            body: JSON.stringify(testPayload)
        });
        console.log(`   Status: ${response.statusCode}`);
        console.log(`   CORS Headers:`, {
            'Access-Control-Allow-Origin': response.headers['access-control-allow-origin'],
            'Access-Control-Allow-Credentials': response.headers['access-control-allow-credentials']
        });
        console.log(`   Response length: ${response.data.length} characters\n`);
        return response.statusCode === 200;
    } catch (error) {
        console.log(`   Error: ${error.message}\n`);
        return false;
    }
}

// Función principal
async function runTests() {
    console.log(`Backend URL: ${BACKEND_URL}`);
    console.log(`Frontend URL: ${FRONTEND_URL}\n`);
    
    const results = {
        healthCheck: await testHealthCheck(),
        preflight: await testPreflightRequest(),
        postRequest: await testPostRequest()
    };
    
    console.log('=== Resultados ===');
    console.log(`Health Check: ${results.healthCheck ? '✅ PASS' : '❌ FAIL'}`);
    console.log(`Preflight Request: ${results.preflight ? '✅ PASS' : '❌ FAIL'}`);
    console.log(`POST Request: ${results.postRequest ? '✅ PASS' : '❌ FAIL'}`);
    
    const allPassed = Object.values(results).every(result => result);
    console.log(`\nConfiguración CORS: ${allPassed ? '✅ CORRECTA' : '❌ NECESITA AJUSTES'}`);
    
    if (!allPassed) {
        console.log('\n=== Recomendaciones ===');
        console.log('1. Verifica que las variables de entorno estén configuradas en Azure');
        console.log('2. Reinicia la App Service después de cambiar la configuración');
        console.log('3. Verifica que el backend esté funcionando correctamente');
        console.log('4. Revisa los logs de la App Service para errores');
    }
}

// Ejecutar las pruebas
runTests().catch(console.error);
