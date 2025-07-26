"use strict";
var __importDefault = (this && this.__importDefault) || function (mod) {
    return (mod && mod.__esModule) ? mod : { "default": mod };
};
Object.defineProperty(exports, "__esModule", { value: true });
// backend/index.ts
const app_1 = __importDefault(require("./src/app"));
// Arrancar el servidor solo si este archivo es ejecutado directamente
if (require.main === module) {
    const PORT = process.env.PORT || 8000;
    app_1.default.listen(PORT, () => {
        console.log(`EvaluaTE backend server running on port ${PORT}`);
    });
}
exports.default = app_1.default;
