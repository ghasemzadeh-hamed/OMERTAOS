-- CreateTable
CREATE TABLE "SystemState" (
    "key" TEXT NOT NULL,
    "boolValue" BOOLEAN NOT NULL DEFAULT false,
    "createdAt" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updatedAt" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT "SystemState_pkey" PRIMARY KEY ("key")
);
