-- ----------------------------
-- Table structure for prompt
-- ----------------------------
DROP TABLE IF EXISTS "prompt";
CREATE TABLE "prompt" (
  "id" SERIAL PRIMARY KEY,
  "uuid" varchar(64) NOT NULL,
  "status" varchar(10) NOT NULL DEFAULT '0',
  "description" text,
  "created_time" timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  "updated_time" timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  "created_id" int4,
  "updated_id" int4,
  "prompt_code" varchar(255) NOT NULL,
  "prompt_title" varchar(100) NOT NULL,
  "version_id" int8,
  "content" text NOT NULL,
  "ability_tags" jsonb,
  "instructions" jsonb,
  "evaluate_result" jsonb,
  "is_publish" int4 NOT NULL DEFAULT 0
);
COMMENT ON TABLE "prompt" IS 'AI助手提示词表';
COMMENT ON COLUMN "prompt"."id" IS '主键ID';
COMMENT ON COLUMN "prompt"."uuid" IS 'UUID全局唯一标识';
COMMENT ON COLUMN "prompt"."status" IS '是否启用(0:启用 1:禁用)';
COMMENT ON COLUMN "prompt"."description" IS '备注/描述';
COMMENT ON COLUMN "prompt"."created_time" IS '创建时间';
COMMENT ON COLUMN "prompt"."updated_time" IS '更新时间';
COMMENT ON COLUMN "prompt"."created_id" IS '创建人ID';
COMMENT ON COLUMN "prompt"."updated_id" IS '更新人ID';
COMMENT ON COLUMN "prompt"."prompt_code" IS '提示词编码';
COMMENT ON COLUMN "prompt"."prompt_title" IS '提示词标题';
COMMENT ON COLUMN "prompt"."version_id" IS '当前版本ID';
COMMENT ON COLUMN "prompt"."content" IS '提示词内容';
COMMENT ON COLUMN "prompt"."ability_tags" IS '能力词云';
COMMENT ON COLUMN "prompt"."instructions" IS '补充提示词指令';
COMMENT ON COLUMN "prompt"."evaluate_result" IS '提示词评估结果';
COMMENT ON COLUMN "prompt"."is_publish" IS '是否发布（0否 1是）';
CREATE UNIQUE INDEX "idx_prompt_uuid" ON "prompt" ("uuid");
CREATE UNIQUE INDEX "idx_prompt_code" ON "prompt" ("prompt_code");

-- ----------------------------
-- Table structure for prompt_version
-- ----------------------------
DROP TABLE IF EXISTS "prompt_version";
CREATE TABLE "prompt_version" (
  "id" SERIAL PRIMARY KEY,
  "uuid" varchar(64) NOT NULL,
  "status" varchar(10) NOT NULL DEFAULT '0',
  "description" text,
  "created_time" timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  "updated_time" timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  "created_id" int4,
  "updated_id" int4,
  "prompt_id" int4 NOT NULL,
  "version" int4 NOT NULL,
  "content" text NOT NULL,
  "ability_tags" jsonb,
  "instructions" jsonb,
  "is_archived" int4 NOT NULL DEFAULT 0
);
COMMENT ON TABLE "prompt_version" IS 'AI助手提示词版本表';
COMMENT ON COLUMN "prompt_version"."id" IS '主键ID';
COMMENT ON COLUMN "prompt_version"."uuid" IS 'UUID全局唯一标识';
COMMENT ON COLUMN "prompt_version"."status" IS '是否启用(0:启用 1:禁用)';
COMMENT ON COLUMN "prompt_version"."description" IS '备注/描述';
COMMENT ON COLUMN "prompt_version"."created_time" IS '创建时间';
COMMENT ON COLUMN "prompt_version"."updated_time" IS '更新时间';
COMMENT ON COLUMN "prompt_version"."created_id" IS '创建人ID';
COMMENT ON COLUMN "prompt_version"."updated_id" IS '更新人ID';
COMMENT ON COLUMN "prompt_version"."prompt_id" IS '提示词ID';
COMMENT ON COLUMN "prompt_version"."version" IS '版本号';
COMMENT ON COLUMN "prompt_version"."content" IS '提示词内容';
COMMENT ON COLUMN "prompt_version"."ability_tags" IS '能力词云';
COMMENT ON COLUMN "prompt_version"."instructions" IS '补充提示词指令';
COMMENT ON COLUMN "prompt_version"."is_archived" IS '是否归档（0否 1是）';
CREATE UNIQUE INDEX "idx_prompt_version_uuid" ON "prompt_version" ("uuid");
