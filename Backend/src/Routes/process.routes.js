import { Router } from "express";
import { test_status } from "../Controllers/process.controller.js";
const router = Router();
router.route("/tstc").post(test_status)
export default router;