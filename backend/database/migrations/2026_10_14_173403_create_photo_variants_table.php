<?php

use Illuminate\Database\Migrations\Migration;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Support\Facades\DB;
use Illuminate\Support\Facades\Schema;

return new class extends Migration
{
    public function up(): void
    {
        Schema::create('photo_variants', function (Blueprint $table) {
            $table->id();
            $table->bigInteger('photo_file_id')->unsigned()->nullable(false);
            $table->string('variant', 32)->nullable(false);
            $table->string('storage_path', 255)->nullable(false)->comment('Chemin relatif au disque (volume ou objet S3, ADR-004)');
            $table->smallInteger('width_px')->unsigned()->nullable(false);
            $table->smallInteger('height_px')->unsigned()->nullable(false);
            $table->timestamp('created_at')->nullable();
            $table->unique(['photo_file_id', 'variant']);
        });

        // Contraintes nommees et FULLTEXT (MySQL >= 8.0.16). Ignores sous SQLite.
        if (DB::getDriverName() === 'mysql') {
            DB::statement("ALTER TABLE photo_variants ADD CONSTRAINT fk_photo_variants_file FOREIGN KEY (photo_file_id) REFERENCES photo_files (id) ON DELETE CASCADE");
        }

        // Contraintes CHECK nommees (MySQL >= 8.0.16). Ignores sous SQLite (tests en memoire).
        if (DB::getDriverName() === 'mysql') {
            DB::statement("ALTER TABLE photo_variants ADD CONSTRAINT ck_photo_variants_variant CHECK (variant IN ('original', 'mobile'))");
            DB::statement("ALTER TABLE photo_variants ADD CONSTRAINT ck_photo_variants_size CHECK (width_px > 0 AND height_px > 0)");
        }

    }

    public function down(): void
    {
        Schema::dropIfExists('photo_variants');
    }
};
