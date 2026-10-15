<?php

use Illuminate\Database\Migrations\Migration;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Support\Facades\DB;
use Illuminate\Support\Facades\Schema;

return new class extends Migration
{
    public function up(): void
    {
        Schema::create('photo_files', function (Blueprint $table) {
            $table->id();
            $table->bigInteger('owner_user_id')->unsigned()->nullable(false)->comment('Compte qui a téléversé (cloisonnement FR-051)');
            $table->string('stored_name', 64)->nullable(false);
            $table->string('non', 255)->nullable();
            $table->string('mime_type', 64)->nullable(false);
            $table->integer('size_bytes')->unsigned()->nullable(false);
            $table->string('check_status', 32)->nullable(false);
            $table->string('rejection_reason', 255)->nullable();
            $table->timestamps();
            $table->unique('stored_name');
            $table->index('owner_user_id');
        });

        // Contraintes nommees et FULLTEXT (MySQL >= 8.0.16). Ignores sous SQLite.
        if (DB::getDriverName() === 'mysql') {
            DB::statement("ALTER TABLE photo_files ADD CONSTRAINT fk_photo_files_owner FOREIGN KEY (owner_user_id) REFERENCES users (id) ON DELETE RESTRICT");
        }

        // Contraintes CHECK nommees (MySQL >= 8.0.16). Ignores sous SQLite (tests en memoire).
        if (DB::getDriverName() === 'mysql') {
            DB::statement("ALTER TABLE photo_files ADD CONSTRAINT ck_photo_files_check_status CHECK (check_status IN ('accepted', 'rejected'))");
            DB::statement("ALTER TABLE photo_files ADD CONSTRAINT ck_photo_files_rejection CHECK (check_status <> 'rejected' OR rejection_reason IS NOT NULL)");
            DB::statement("ALTER TABLE photo_files ADD CONSTRAINT ck_photo_files_size CHECK (size_bytes > 0)");
        }

    }

    public function down(): void
    {
        Schema::dropIfExists('photo_files');
    }
};
