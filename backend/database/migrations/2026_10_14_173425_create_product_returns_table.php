<?php

use Illuminate\Database\Migrations\Migration;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Support\Facades\DB;
use Illuminate\Support\Facades\Schema;

return new class extends Migration
{
    public function up(): void
    {
        Schema::create('product_returns', function (Blueprint $table) {
            $table->id();
            $table->bigInteger('order_line_id')->unsigned()->nullable(false)->comment('un retour par produit (RG-030)');
            $table->integer('quantity')->nullable(false);
            $table->string('reason', 32)->nullable(false)->comment('motif : MotifRetour');
            $table->bigInteger('photo_file_id')->unsigned()->nullable()->comment('photo [0..1] (HYPOTHÈSE)');
            $table->string('refund_method', 32)->nullable(false)->comment('moyenRemboursement');
            $table->text('refund_details')->nullable(false);
            $table->string('chiffré', 255)->nullable();
            $table->timestamp('requested_at')->nullable(false)->comment('dateDemande (RG-019 : <= received_at + 7 j, vérifié par le service)');
            $table->string('status', 32)->nullable(false)->default('requested');
            $table->timestamps();
            $table->index('order_line_id');
            $table->index(['status', 'requested_at']);
        });

        // Contraintes nommees et FULLTEXT (MySQL >= 8.0.16). Ignores sous SQLite.
        if (DB::getDriverName() === 'mysql') {
            DB::statement("ALTER TABLE product_returns ADD CONSTRAINT fk_product_returns_order_line FOREIGN KEY (order_line_id) REFERENCES order_lines (id) ON DELETE RESTRICT");
            DB::statement("ALTER TABLE product_returns ADD CONSTRAINT fk_product_returns_photo FOREIGN KEY (photo_file_id) REFERENCES photo_files (id) ON DELETE RESTRICT");
        }

        // Contraintes CHECK nommees (MySQL >= 8.0.16). Ignores sous SQLite (tests en memoire).
        if (DB::getDriverName() === 'mysql') {
            DB::statement("ALTER TABLE product_returns ADD CONSTRAINT ck_product_returns_quantity CHECK (quantity > 0)");
            DB::statement("ALTER TABLE product_returns ADD CONSTRAINT ck_product_returns_reason CHECK (reason IN ('change_of_mind', 'defective', 'incorrect', 'not_as_described'))");
            DB::statement("ALTER TABLE product_returns ADD CONSTRAINT ck_product_returns_refund_method CHECK (refund_method IN ('bank_transfer', 'other_traceable'))");
            DB::statement("ALTER TABLE product_returns ADD CONSTRAINT ck_product_returns_status CHECK (status IN ('requested', 'pickup_in_progress', 'picked_up', 'verified_by_seller', 'disputed', 'in_dispute', 'customer_refunded', 'return_refused'))");
        }

    }

    public function down(): void
    {
        Schema::dropIfExists('product_returns');
    }
};
