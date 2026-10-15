<?php

use Illuminate\Database\Migrations\Migration;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Support\Facades\DB;
use Illuminate\Support\Facades\Schema;

return new class extends Migration
{
    public function up(): void
    {
        Schema::create('product_photos', function (Blueprint $table) {
            $table->id();
            $table->bigInteger('product_id')->unsigned()->nullable(false);
            $table->bigInteger('photo_file_id')->unsigned()->nullable(false);
            $table->smallInteger('position')->unsigned()->nullable(false)->default(0);
            $table->timestamp('created_at')->nullable();
            $table->unique('photo_file_id');
            $table->index(['product_id', 'position']);
        });

        // Contraintes nommees et FULLTEXT (MySQL >= 8.0.16). Ignores sous SQLite.
        if (DB::getDriverName() === 'mysql') {
            DB::statement("ALTER TABLE product_photos ADD CONSTRAINT fk_product_photos_product FOREIGN KEY (product_id) REFERENCES products (id) ON DELETE RESTRICT");
            DB::statement("ALTER TABLE product_photos ADD CONSTRAINT fk_product_photos_file FOREIGN KEY (photo_file_id) REFERENCES photo_files (id) ON DELETE RESTRICT");
        }

    }

    public function down(): void
    {
        Schema::dropIfExists('product_photos');
    }
};
