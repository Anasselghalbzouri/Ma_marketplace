<?php

use Illuminate\Database\Migrations\Migration;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Support\Facades\DB;
use Illuminate\Support\Facades\Schema;

return new class extends Migration
{
    public function up(): void
    {
        Schema::create('reviews', function (Blueprint $table) {
            $table->id();
            $table->bigInteger('customer_id')->unsigned()->nullable(false)->comment('Client rédige Avis');
            $table->bigInteger('order_line_id')->unsigned()->nullable(false)->comment('Avis porte sur LigneCommande');
            $table->bigInteger('product_id')->unsigned()->nullable(false);
            $table->tinyInteger('rating')->unsigned()->nullable(false)->comment('note 1..5 (HYPOTHÈSE F012)');
            $table->text('comment')->nullable();
            $table->boolean('is_hidden')->nullable(false)->default(false)->comment('masqué (RG-015)');
            $table->timestamp('hidden_at')->nullable();
            $table->timestamps();
            $table->unique('order_line_id');
            $table->index(['product_id', 'is_hidden', 'rating']);
            $table->index('customer_id');
        });

        // Contraintes nommees et FULLTEXT (MySQL >= 8.0.16). Ignores sous SQLite.
        if (DB::getDriverName() === 'mysql') {
            DB::statement("ALTER TABLE reviews ADD CONSTRAINT fk_reviews_customer FOREIGN KEY (customer_id) REFERENCES customers (id) ON DELETE RESTRICT");
            DB::statement("ALTER TABLE reviews ADD CONSTRAINT fk_reviews_order_line FOREIGN KEY (order_line_id, product_id) REFERENCES order_lines (id, product_id) ON DELETE RESTRICT");
            DB::statement("ALTER TABLE reviews ADD CONSTRAINT fk_reviews_product FOREIGN KEY (product_id) REFERENCES products (id) ON DELETE RESTRICT");
        }

        // Contraintes CHECK nommees (MySQL >= 8.0.16). Ignores sous SQLite (tests en memoire).
        if (DB::getDriverName() === 'mysql') {
            DB::statement("ALTER TABLE reviews ADD CONSTRAINT ck_reviews_rating_range CHECK (rating BETWEEN 1 AND 5)");
            DB::statement("ALTER TABLE reviews ADD CONSTRAINT ck_reviews_hidden_at CHECK (is_hidden = FALSE OR hidden_at IS NOT NULL)");
        }

    }

    public function down(): void
    {
        Schema::dropIfExists('reviews');
    }
};
