# 📌 CHECKLIST DE ACCIÓN INMEDIATA

**Versión:** MVP Audit - 2026-09-01  
**Estado:** BLOQUEADO PARA PRODUCCIÓN  
**Tiempo estimado de fixes:** 48-72 horas

---

## 🚨 HOY (Próximas 2 horas)

### ✅ SEGURIDAD CRÍTICA

```bash
# 1. Revocar TODAS las API keys
# - Google Cloud Console: https://console.cloud.google.com/apis/credentials
#   → Eliminar keys que estaban expuestas (ver .env local)
# - Groq: https://console.groq.com/settings
#   → Revocar keys expuestas (ver .env local)
# - TiDB: Cambiar contraseña (credenciales estaban expuestas)
# - MinIO: Cambiar credenciales de acceso (valores por defecto comprometidos)

# 2. Verificar si .env está en Git
git log --all --full-history -- "backend/.env" | head -20

# 3. Purgar del historio Git (IMPORTANTE)
git filter-branch --tree-filter 'rm -f backend/.env' -- --all
git push origin --force --all

# 4. Generar nuevas claves seguras
python3 << 'EOF'
import secrets
import json

keys = {
    "SECRET_KEY": secrets.token_urlsafe(32),
    "MINIO_SECRET_KEY": secrets.token_urlsafe(16),
    "GEMINI_KEY_1": "OBTENER_DE_GOOGLE_CLOUD",  # NUEVO
    "GROQ_API_KEY": "OBTENER_DE_GROQ_CONSOLE",  # NUEVO
}

for k, v in keys.items():
    print(f"{k}={v}")
EOF

# 5. Actualizar .env con nuevas claves y agregar a .gitignore
echo "backend/.env" >> .gitignore
git add .gitignore
git commit -m "chore: ensure .env is never tracked"
```

---

### ✅ CODE FIXES CRÍTICOS

**A. Sanitizar HTML en PDF** (30 min)
```bash
pip install bleach==6.1.0
```
Editar `backend/pdf_service.py` línea 44-72 (ver documento PRODUCTION_READINESS_AUDIT.md)

**B. Implementar Rate Limiting** (1 hora)
```bash
pip install slowapi==0.1.9
```
Editar `backend/main.py` (agregar código en documento PRODUCTION_READINESS_AUDIT.md)

---

## 🗓️ MAÑANA (Día 2 - 8 horas)

### ✅ GDPR CRÍTICO

- [ ] Crear componente ConsentForm con checkboxes 50x50px
- [ ] Implementar `/api/user/{user_id}/data` (GET)
- [ ] Implementar `/api/user/{user_id}/delete` (DELETE)
- [ ] Implementar `/api/user/{user_id}/export` (GET CSV)
- [ ] Actualizar política de privacidad con detalles GDPR

**Archivos a crear:**
- `nuevo-frontend/src/components/ConsentForm.tsx` (nuevo)
- Endpoints en `backend/main.py`

---

### ✅ SECURITY HEADERS (30 min)

Agregar middleware en `backend/main.py` para CSP, X-Frame-Options, etc.

---

## 📅 SEMANA 1 (Completa)

### Prioridad 1 - CRÍTICA (24 horas)

| Tarea | Tiempo | Responsable | Status |
|-------|--------|-------------|--------|
| Revocar API keys | 1h | DevOps | ❌ |
| Purgar .env de Git | 1h | DevOps | ❌ |
| Sanitizar HTML | 1h | Backend | ❌ |
| Rate limiting | 1h | Backend | ❌ |
| Security headers | 0.5h | Backend | ❌ |
| Endpoints GDPR | 4h | Backend/Frontend | ❌ |
| Consentimientos UI | 2h | Frontend | ❌ |
| Health endpoints | 1h | Backend | ❌ |
| Prometheus metrics | 2h | Backend | ❌ |
| Tests endpoints | 2h | QA | ❌ |
| TOTAL | **15.5h** | | |

---

### Prioridad 2 - ACCESIBILIDAD (12 horas)

**Must Fix (nivel A):**
- [ ] GameCard → button (0.5h)
- [ ] CookieConsent → focus trap (1h)
- [ ] DragDropScene → keyboard (2h)
- [ ] ChoiceScene → buttons (1h)
- [ ] WelcomePage → focus rings (0.5h)
- [ ] RadarChart → aria-label + tabla (1.5h)
- [ ] Icons → aria-label (0.5h)
- [ ] UploadCVPage → aria-describedby (0.5h)

**Tiempo total: 7.5h**

---

## ✅ VALIDACIONES REQUERIDAS

### Validación Legal (GDPR)
- [ ] Abogado especialista GDPR revisa consentimientos
- [ ] Verifica DPA con Google Gemini
- [ ] Confirma cumplimiento Art. 15, 17, 20

### Validación Seguridad
- [ ] Ejecutar `bandit -r backend/` (detección de vulnerabilidades)
- [ ] Ejecutar `safety check` (CVEs en dependencias)
- [ ] Security audit externo (2-5k€)

### Validación Accesibilidad
- [ ] Usar WAVE extension en todos los componentes
- [ ] Pruebas con NVDA screen reader
- [ ] Pruebas con navegación solo teclado (Tab + Enter)
- [ ] Auditoría externa WCAG 2.2 AA (1-2k€)

---

## 🔄 PROCESS DE DEPLOYMENT (Cuando todo esté OK)

```bash
# 0. Verificar no hay cambios locales
git status  # Debe estar clean

# 1. Crear branch de release
git checkout -b release/v1.0.0-preproduction

# 2. Ejecutar tests
cd backend && pytest tests/ -v && cd ..
cd nuevo-frontend && npm test && cd ..

# 3. Security scanning
pip install bandit safety
bandit -r backend/ -ll -f json > security-report.json
safety check --json > dependencies-report.json

# 4. Accessibility audit
cd nuevo-frontend
npm run build  # Verificar no hay errores
cd ..

# 5. Build Docker
docker build -f backend/Dockerfile -t evaluate:v1.0.0 .
docker push evaluate:v1.0.0

# 6. Deploy a staging (si tienes)
# kubectl apply -f k8s/staging/ --kubeconfig=...

# 7. Smoke tests en staging
# curl https://staging.evaluate.teamworkz.co/health/ready

# 8. Crear pull request para revisión
git push origin release/v1.0.0-preproduction
# → Pedir reviews de arquitecto + security + legal

# 9. Una vez aprovado, merge a main
git checkout main
git pull
git merge --no-ff release/v1.0.0-preproduction
git tag -a v1.0.0 -m "Production ready - Security + GDPR + Accesibilidad"
git push origin main --tags

# 10. Deploy a producción
# docker pull evaluate:v1.0.0
# kubectl apply -f k8s/production/ --kubeconfig=...
```

---

## 📞 CONTACTOS DE EMERGENCIA

Si encuentras otros problemas críticos:

- **Seguridad:** security@teamworkz.co
- **GDPR Legal:** legal@teamworkz.co  
- **Accesibilidad:** accessibility@teamworkz.co
- **DevOps:** devops@teamworkz.co

---

## 📚 DOCUMENTOS GENERADOS

1. **PRODUCTION_READINESS_AUDIT.md** - Auditoría completa de seguridad, GDPR, arquitectura
2. **ACCESSIBILITY_AUDIT.md** - Detalles de todos los 25 problemas WCAG 2.2
3. **DEPLOYMENT_CHECKLIST.md** (este documento) - Pasos acción inmediata

---

## ⚠️ RIESGOS SI NO SE IMPLEMENTAN LOS FIXES

| Riesgo | Severidad | Consecuencia |
|--------|-----------|-------------|
| API keys expuestas | CRÍTICA | Acceso no autorizado a Google, Groq, DB, MinIO |
| XSS en PDF | CRÍTICA | Inyección de malware, robo de cookies |
| GDPR no cumplido | CRÍTICA | Multas €20M + cierre en Europa |
| Sin rate limiting | ALTA | DDoS attacks y caída de servicio |
| Sin observabilidad | ALTA | Imposible detectar problemas en prod |
| Inaccesible | MEDIA | Demandas de discriminación, WCAG incumplimiento |

---

## ✨ PRÓXIMAS FASES (Después MVP)

**Fase 2 (Semanas 2-4):** Production Infrastructure
- [ ] Terraform/Pulumi para IaC
- [ ] Disaster recovery + backups
- [ ] Load balancing y auto-scaling
- [ ] CDN para assets estáticos

**Fase 3 (Semanas 5-8):** Advanced Observability
- [ ] Distributed tracing (Jaeger)
- [ ] Alerting (PagerDuty)
- [ ] Cost tracking (FinOps)
- [ ] Performance monitoring (Datadog/New Relic)

**Fase 4 (Sprint siguiente):** Security Hardening
- [ ] WAF (Web Application Firewall)
- [ ] Penetration testing
- [ ] SAST/DAST automatizado
- [ ] SOC 2 compliance

---

**Firma digital:** Senior Technical Team  
**Fecha:** 2026-09-01  
**Validez:** 30 días (requiere re-auditoría después)
